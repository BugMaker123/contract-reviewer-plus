import pytest
from httpx import AsyncClient, ASGITransport
from contract_app.bootstrap.app_factory import create_app
from contract_app.modules.documents.application.docx_service import docx_service
from contract_app.infrastructure.storage.file_storage import file_storage
from contract_app.infrastructure.persistence.repositories import repo_store

@pytest.mark.asyncio
async def test_uploaded_contract_with_checklists():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Create a realistic contract docx with various clauses
        clauses = [
            "一、合作宗旨与前提",
            "1.1 本协议自签署之日起生效，双方均具备合法资质。",
            "二、交货时间与验收标准",
            "2.1 甲方应于每月15日前交货，逾期交货每日按逾期金额0.2%支付违约金。",
            "2.2 乙方收到货物后应在3日内验收，未出具验收报告不得视为合格。",
            "三、货款结算与支付方式",
            "3.1 乙方在收到货物后付款，具体付款时间另行协商。",
            "四、违约赔偿与责任限制",
            "4.1 任何一方违约，应赔偿守约方的全部损失且不设上限。",
            "五、合同解除",
            "5.1 任何一方均可随时解除本协议且无需提前通知对方。",
            "六、争议解决管辖",
            "6.1 发生争议协商不成的，应向对方所在地有管辖权的人民法院提起诉讼。"
        ]
        obj_key, _ = docx_service.create_sample_docx("商业采购合作协议", clauses)
        docx_bytes = file_storage.read_file(obj_key)

        # 2. Get available categories and checklists
        cat_res = await client.get("/api/categories")
        categories = cat_res.json()["items"]
        cat_id = categories[0]["id"]

        chk_res = await client.get(f"/api/checklists?category_id={cat_id}")
        checklists = chk_res.json()["items"]
        assert len(checklists) > 0
        selected_chk_ids = [c["id"] for c in checklists[:3]]

        # 3. Upload file and bind checklists
        res = await client.post(
            "/api/contracts",
            data={
                "title": "商业采购合作协议",
                "category_id": cat_id,
                "checklist_ids": str(selected_chk_ids).replace("'", '"')
            },
            files={"file": ("commercial_purchase.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        )
        assert res.status_code == 200
        contract = res.json()["contract"]
        contract_id = contract["id"]
        assert contract["title"] == "商业采购合作协议"
        assert len(contract["checklist_ids"]) == len(selected_chk_ids)

        # 4. Verify document structure extraction
        struct_res = await client.get(f"/api/documents/{contract['head_version_id']}/structure")
        assert struct_res.status_code == 200
        blocks = struct_res.json()["blocks"]
        assert len(blocks) >= len(clauses)
        # Verify enhanced regex extracts clause numbering
        clause_ids = [b["clause_id"] for b in blocks]
        assert any("一、" in cid for cid in clause_ids)
        assert any("2.1" in cid for cid in clause_ids)
        assert any("4.1" in cid for cid in clause_ids)

        # 5. Start review run and verify execution
        run_res = await client.post("/api/review-runs", json={
            "contract_id": contract_id,
            "stance": "我方(受托方)"
        })
        assert run_res.status_code == 202
        run_id = run_res.json()["run_id"]

        # Run pipeline
        from contract_app.modules.reviews.application.run_pipeline import run_pipeline_use_case
        await run_pipeline_use_case.execute(run_id)

        # 6. Verify review findings match the selected checklists and clauses
        ig_res = await client.get(f"/api/review-runs/{run_id}/issue-groups")
        assert ig_res.status_code == 200
        issues = ig_res.json()["issue_groups"]
        assert len(issues) >= 2

        # Verify evidence, proposals and replacement operations exist
        plan = ig_res.json()["plan"]
        assert plan is not None
        assert len(plan["operations"]) >= 2
        for op in plan["operations"]:
            assert op["expected_text"] is not None
            assert op["replacement_text"] is not None
