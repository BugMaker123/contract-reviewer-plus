import pytest
from httpx import AsyncClient, ASGITransport
from contract_app.bootstrap.app_factory import create_app

@pytest.mark.asyncio
async def test_categories_and_checklists_crud():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. List initial categories
        res = await client.get("/api/categories")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] >= 3
        first_cat_id = data["items"][0]["id"]

        # 2. Create new category
        res = await client.post("/api/categories", json={
            "name": "劳动人事与劳务协议类",
            "code": "HR_LABOR",
            "description": "员工保密、竞业限制及高级聘用合同",
            "sort_order": 10
        })
        assert res.status_code == 200
        new_cat = res.json()["category"]
        new_cat_id = new_cat["id"]

        # 3. Create checklist item bound to this category
        res = await client.post("/api/checklists", json={
            "category_id": new_cat_id,
            "title": "竞业限制补偿金标准约定",
            "risk_level": "medium",
            "standard_clause": "离职后竞业补偿金不低于离职前月平均工资的30%且不低于当地最低工资标准。",
            "check_prompt": "防范因补偿金约定缺失导致竞业限制条款无效风险",
            "is_enabled": True,
            "sort_order": 1
        })
        assert res.status_code == 200
        chk = res.json()["item"]
        assert chk["category_id"] == new_cat_id
        chk_id = chk["id"]

        # 4. Verify cannot delete category when checklist exists
        del_cat_res = await client.delete(f"/api/categories/{new_cat_id}")
        assert del_cat_res.status_code == 400

        # 5. Delete checklist item
        del_chk_res = await client.delete(f"/api/checklists/{chk_id}")
        assert del_chk_res.status_code == 200

        # 6. Now can delete category
        del_cat_ok = await client.delete(f"/api/categories/{new_cat_id}")
        assert del_cat_ok.status_code == 200

        # 7. Verify creating contract without file is rejected with 400
        no_file_res = await client.post("/api/contracts", data={"title": "无文件合同"})
        assert no_file_res.status_code == 400

        # 8. Create contract with category, checklist and valid docx file
        from contract_app.modules.documents.application.docx_service import docx_service
        from contract_app.infrastructure.storage.file_storage import file_storage
        dummy_key, _ = docx_service.create_sample_docx("测试技术协议", ["第一条 合作约定"])
        dummy_bytes = file_storage.read_file(dummy_key)

        contract_res = await client.post(
            "/api/contracts",
            data={
                "title": "测试技术协议",
                "category_id": first_cat_id,
                "checklist_ids": '["chk_001"]'
            },
            files={"file": ("test_contract.docx", dummy_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        )
        assert contract_res.status_code == 200
        c_data = contract_res.json()["contract"]
        assert c_data["category_id"] == first_cat_id
        assert "chk_001" in c_data["checklist_ids"]
        assert len(c_data["focus_areas"]) > 0
