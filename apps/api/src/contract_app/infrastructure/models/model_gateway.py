from typing import List, Dict, Any, Optional
import json
import httpx
from contract_app.bootstrap.config import settings

class ModelGateway:
    def __init__(self):
        self.api_base = settings.openai_api_base
        self.api_key = settings.openai_api_key
        self.model = settings.openai_model
        self.mock_mode = settings.mock_ai_pipeline or not bool(self.api_key)

    async def analyze_blocks(
        self,
        blocks: List[Dict[str, Any]],
        stance: str = "我方",
        focus_areas: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        if not self.mock_mode and self.api_key:
            try:
                return await self._call_llm_analyze(blocks, stance, focus_areas)
            except Exception as e:
                # In strict mode per spec: don't silently pretend if explicit remote call failed
                raise RuntimeError(f"Remote LLM call failed: {e}")
        return self._intelligent_legal_analyze(blocks, stance)

    async def _call_llm_analyze(
        self,
        blocks: List[Dict[str, Any]],
        stance: str,
        focus_areas: Optional[List[str]]
    ) -> List[Dict[str, Any]]:
        prompt = (
            f"作为企业法务专家，请从【{stance}】立场审查以下合同条款。\n"
            f"重点关注领域：{focus_areas or '全面合规风险'}\n"
            "输出结构化 JSON 数组，每个元素包含：\n"
            "clause_id, title, severity(high/medium/low), evidence(原文), "
            "public_analysis(法律分析), proposal(修改建议), "
            "expected_text(需替换原文), replacement_text(修改后文本)\n\n"
            f"合同条款如下：\n{json.dumps(blocks, ensure_ascii=False)}"
        )
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{self.api_base}/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            # Extract JSON block
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            return json.loads(content)

    def _intelligent_legal_analyze(
        self,
        blocks: List[Dict[str, Any]],
        stance: str
    ) -> List[Dict[str, Any]]:
        findings = []
        for b in blocks:
            text = b["text"]
            cid = b["clause_id"]

            # 1. 违约责任与赔偿上限
            if "违约" in text and ("全部损失" in text or "不设上限" in text or "无条件赔偿" in text):
                findings.append({
                    "clause_id": cid,
                    "title": "违约赔偿责任未设定合理上限与间接损失排除",
                    "severity": "high",
                    "evidence": text,
                    "public_analysis": "条款约定赔偿全部直接与间接损失且未设赔偿限额，对我方构成不可预计的无限连带与重大经营风险。",
                    "proposal": "增加间接损失与商业利润损失排除条款，并将总赔偿责任限制在合同总金额的 100% 以内。",
                    "expected_text": text,
                    "replacement_text": text.replace("全部损失", "因本合同引起的直接经济损失（累计不超过本合同总价款金额，且不包括利润损失、商业信誉损失等间接损失）")
                })
            # 2. 单方解除权与无条件解约
            elif "解除" in text and ("单方随时解除" in text or "无条件解除" in text or "无需通知" in text):
                findings.append({
                    "clause_id": cid,
                    "title": "单方任意解除权失衡且缺乏合理宽限期",
                    "severity": "high",
                    "evidence": text,
                    "public_analysis": "对方保留单方无条件随时解约权利，严重破坏履约确定性与交易稳定性，且未给予任何补救宽限期。",
                    "proposal": "增加至少 15 个工作日的书面催告整改期，逾期未改善方可触发解除。",
                    "expected_text": text,
                    "replacement_text": text + "（任何一方行使前述解除权前，应给予对方不少于十五（15）个工作日的书面催告与整改宽限期）。"
                })
            # 3. 付款期限不明确与延期苛刻利息
            elif "付款" in text and ("视情况" in text or "另行协商" in text or "合理时间" in text or "日万分之五" in text):
                findings.append({
                    "clause_id": cid,
                    "title": "付款时限约定模糊或逾期利息过高",
                    "severity": "medium",
                    "evidence": text,
                    "public_analysis": "付款节点未约定明确工作日时限，将导致验收后回款流程无限期拖延；逾期利息标准过高存在被诉风险。",
                    "proposal": "明确验收合格及收到合规发票后 15 个工作日内支付，逾期利息下调为同期 LPR 标准。",
                    "expected_text": text,
                    "replacement_text": text.replace("视情况", "在收到合规增值税专用发票后十五（15）个工作日内").replace("另行协商", "按中国人民银行授权全国银行间同业拆借中心公布的同期一年期贷款市场报价利率（LPR）计算")
                })
            # 4. 知识产权归属
            elif "知识产权" in text and ("全部归对方所有" in text or "包含既有知识产权" in text or "无偿转让" in text):
                findings.append({
                    "clause_id": cid,
                    "title": "既有背景知识产权归属与成果权利让渡失衡",
                    "severity": "high",
                    "evidence": text,
                    "public_analysis": "原条款将包含我方既有技术储备（Background IP）在内的全部成果所有权无偿让渡，存在核心资产流失风险。",
                    "proposal": "明确各方签约前已拥有的知识产权仍归各自所有，本次合作新产生的定制开发成果按约定享有使用权或排他许可。",
                    "expected_text": text,
                    "replacement_text": "除各方在签约前已独立享有的背景知识产权（Background IP）仍归原权利人所有外，" + text
                })
            # 5. 管辖争议
            elif "争议" in text or "诉讼" in text or "仲裁" in text:
                if "对方所在地" in text:
                    findings.append({
                        "clause_id": cid,
                        "title": "争议管辖地对我方不利",
                        "severity": "low",
                        "evidence": text,
                        "public_analysis": "管辖法院约定为对方所在地人民法院，增加我方后续维权差旅与诉讼成本。",
                        "proposal": "建议修改为原告所在地人民法院管辖或双方所在地有管辖权的人民法院。",
                        "expected_text": "对方所在地",
                        "replacement_text": "原告住所地"
                    })

        # If no specific risk matched but clauses exist, provide baseline standard review finding
        if not findings and blocks:
            first_b = blocks[0]
            findings.append({
                "clause_id": first_b["clause_id"],
                "title": "合同首部主体资格与授权代表确认",
                "severity": "low",
                "evidence": first_b["text"],
                "public_analysis": "建议核对签约主体的营业执照有效存续状态及法定代表人/授权代表的合法书面授权文件。",
                "proposal": "在合同末尾附件补充法定代表人身份证明及授权委托书复印件。",
                "expected_text": first_b["text"],
                "replacement_text": first_b["text"] + "（附：双方主体资格及授权委托文件）"
            })
        return findings

model_gateway = ModelGateway()
