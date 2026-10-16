from typing import List, Dict, Any, Optional
import json
import re
import httpx
from contract_app.bootstrap.config import settings

class ModelGateway:
    def __init__(self):
        self._refresh_provider_config()

    def _refresh_provider_config(self):
        self.provider = (settings.llm_provider or "deepseek").lower()
        if self.provider == "deepseek":
            self.api_base = settings.deepseek_api_base.rstrip("/")
            self.api_key = settings.deepseek_api_key
            self.model = settings.deepseek_model or "deepseek-v4-flash"
        elif self.provider == "qwen":
            self.api_base = "https://dashscope.aliyuncs.com/compatible-mode/v1"
            self.api_key = settings.dashscope_api_key
            self.model = settings.qwen_model or "qwen-plus"
        else:
            self.api_base = settings.openai_api_base.rstrip("/")
            self.api_key = settings.openai_api_key
            self.model = settings.openai_model or "gpt-4o"

        self.mock_mode = settings.mock_ai_pipeline or not bool(self.api_key)

    async def call_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> str:
        self._refresh_provider_config()
        if self.mock_mode or not self.api_key:
            return ""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        async with httpx.AsyncClient(timeout=90.0) as client:
            resp = await client.post(f"{self.api_base}/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def analyze_blocks(
        self,
        blocks: List[Dict[str, Any]],
        stance: str = "我方",
        focus_areas: Optional[List[str]] = None,
        checklists: Optional[List[Any]] = None
    ) -> List[Dict[str, Any]]:
        self._refresh_provider_config()
        if not self.mock_mode and self.api_key:
            try:
                return await self._call_llm_analyze(blocks, stance, focus_areas, checklists)
            except Exception as e:
                print(f"[ModelGateway] Remote LLM ({self.provider}/{self.model}) failed, falling back to intelligent rule engine: {e}")
                return self._intelligent_legal_analyze(blocks, stance, focus_areas, checklists)
        return self._intelligent_legal_analyze(blocks, stance, focus_areas, checklists)

    async def _call_llm_analyze(
        self,
        blocks: List[Dict[str, Any]],
        stance: str,
        focus_areas: Optional[List[str]],
        checklists: Optional[List[Any]]
    ) -> List[Dict[str, Any]]:
        chk_desc = ""
        if checklists:
            chk_lines = []
            for c in checklists:
                c_title = getattr(c, 'title', '')
                c_risk = getattr(c, 'risk_level', 'medium')
                c_pt = getattr(c, 'prompt_template', '') or getattr(c, 'check_prompt', '')
                c_std = getattr(c, 'standard_clause', '')
                chk_lines.append(
                    f"- 审查清单【{c_title}】(风险级别: {c_risk})：\n"
                    f"  业务定制 Prompt 审查指令: {c_pt}\n"
                    f"  参考标准示范条款: {c_std}"
                )
            chk_desc = "\n业务审查清单与定制 Prompt 指令集如下：\n" + "\n".join(chk_lines)

        system_prompt = (
            f"你是企业法务专家审查系统，深度结合 DeepSeek 与国内合规法典体系。\n"
            f"当前审查立场：【{stance}】。\n"
            f"当前使用的 AI 推理引擎：【{self.provider.upper()} - {self.model}】。"
        )
        user_prompt = (
            f"请从【{stance}】立场深度审查以下真实合同条款。\n"
            f"业务关注重点：{focus_areas or '全面合规风险'}\n"
            f"{chk_desc}\n"
            "请严格对照上述审查清单标准与合同原文进行条款级风险研判。\n"
            "输出结构化 JSON 数组，每个元素包含：\n"
            "clause_id (对应条款编号如'五、付款时间'或'1.1'或'段落 3'), "
            "title (风险名称简述), severity ('high'|'medium'|'low'), "
            "evidence (合同中对应有风险的原文段落或语句), "
            "public_analysis (法律专业分析与风险成因阐述), "
            "proposal (具体的商务谈判或修改建议), "
            "expected_text (建议替换的原文片段), "
            "replacement_text (修改后的修订推荐表述)\n\n"
            f"待审查合同段落列表：\n{json.dumps(blocks[:120], ensure_ascii=False)}"
        )
        content = await self.call_chat(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1
        )
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        return json.loads(content)

    def _intelligent_legal_analyze(
        self,
        blocks: List[Dict[str, Any]],
        stance: str,
        focus_areas: Optional[List[str]] = None,
        checklists: Optional[List[Any]] = None
    ) -> List[Dict[str, Any]]:
        findings = []
        matched_block_indices = set()

        # Helper to find best matching block for keywords
        def find_best_blocks(keywords: List[str], exclude_matched: bool = False) -> List[tuple[int, Dict[str, Any]]]:
            scored = []
            for idx, b in enumerate(blocks):
                if exclude_matched and idx in matched_block_indices:
                    continue
                txt = b["text"]
                score = sum(1 for kw in keywords if kw in txt)
                if score > 0:
                    scored.append((score, idx, b))
            scored.sort(key=lambda x: x[0], reverse=True)
            return [(idx, b) for score, idx, b in scored]

        # 1. Process specific Checklist Items
        if checklists:
            for chk in checklists:
                title = getattr(chk, "title", "")
                risk_level = getattr(chk, "risk_level", "high")
                std_clause = getattr(chk, "standard_clause", "")
                prompt_hint = getattr(chk, "check_prompt", "")

                # 1.1 付款 / 验收 先决条件
                if any(w in title for w in ["付款", "验收", "结算", "账期", "对账"]):
                    candidates = find_best_blocks(["付款", "货款", "支付", "结算", "验收", "发票"], exclude_matched=True)
                    if candidates:
                        idx, b = candidates[0]
                        matched_block_indices.add(idx)
                        txt = b["text"]
                        cid = b["clause_id"]
                        
                        # 检查是否缺失验收单或发票先决条件
                        if "验收" not in txt or "发票" not in txt or "报告" not in txt:
                            findings.append({
                                "clause_id": cid,
                                "title": f"{title}：付款条款未明确绑定阶段性合格验收凭据与合规发票",
                                "severity": risk_level,
                                "evidence": txt,
                                "public_analysis": f"根据审查清单要求【{title}】，当前付款约定缺乏明确的合格交付验收报告及合规增值税发票先决条件，容易导致付款与实际交付脱节，形成货款已付但标的物存在重大隐蔽瑕疵的失控风险。",
                                "proposal": prompt_hint or "建议增加：款项支付以双方书面签署的合格验收报告及收到全额合规增值税发票为前置付款条件。",
                                "expected_text": txt,
                                "replacement_text": txt + "（特别约定：任何一笔款项的支付，均以乙方提交书面交付验收报告并经甲方签字确认合格，且收到乙方开具的相应金额合规增值税发票为前提条件）。"
                            })
                        else:
                            findings.append({
                                "clause_id": cid,
                                "title": f"{title}：付款与对账时限建议进一步明确合理工作日宽限",
                                "severity": "medium",
                                "evidence": txt,
                                "public_analysis": f"已约定付款要求，但时限约定仍需细化。核查要点：{prompt_hint or '确认支付节点与争议核对期限清晰'}。",
                                "proposal": "细化验收后付款期限为 15 个工作日，明确争议期间暂停计息。",
                                "expected_text": txt,
                                "replacement_text": txt + "（付款时限明确为验收合格并收到合规发票后十五（15）个工作日内完成划拨）。"
                            })

                # 1.2 违约金责任上限与直接损失界定
                elif any(w in title for w in ["违约金", "赔偿上限", "损失界定", "连带责任"]):
                    candidates = find_best_blocks(["违约", "全部损失", "不设上限", "赔偿", "承担", "罚没"], exclude_matched=True)
                    if candidates:
                        idx, b = candidates[0]
                        matched_block_indices.add(idx)
                        txt = b["text"]
                        cid = b["clause_id"]
                        findings.append({
                            "clause_id": cid,
                            "title": f"{title}：违约赔偿责任未明确封顶上限并排除间接损失",
                            "severity": risk_level,
                            "evidence": txt,
                            "public_analysis": f"审查清单【{title}】重点提示：{prompt_hint or '防范无上限连带赔偿与惩罚性过高违约金'}。现行条款未设置单方累计最高赔偿限额，且未明确剔除预期利润、商业信誉损失等间接损失，严重偏离商业合同对等救济原则。",
                            "proposal": "增加间接损失排除条款，将累计违约赔偿总额严格限定在合同总价款的 100%（或所涉标的额 20%）以内。",
                            "expected_text": txt,
                            "replacement_text": txt + "（但任何一方因违约承担的赔偿责任累计不得超过本合同总金额的100%，且赔偿范围仅限守约方的直接实际经济损失，明确排除任何预期利润、商业机会及间接衍生损失）。"
                        })

                # 1.3 既有背景知识产权及衍生权属
                elif any(w in title for w in ["知识产权", "专利", "源码", "背景知识产权", "权属"]):
                    candidates = find_best_blocks(["知识产权", "专利", "著作权", "源代码", "保密", "成果"], exclude_matched=True)
                    if candidates:
                        idx, b = candidates[0]
                        matched_block_indices.add(idx)
                        txt = b["text"]
                        cid = b["clause_id"]
                        findings.append({
                            "clause_id": cid,
                            "title": f"{title}：签约前既有背景资产知识产权及通用底层工具权属须明确保留",
                            "severity": risk_level,
                            "evidence": txt,
                            "public_analysis": f"依据【{title}】标准要求，需确认各方签约前已拥有的既有技术储备（Background IP）不随本合同转让。原条款权属让渡范围宽泛，存在核心自有资产及商业诀窍被剥夺的潜在风险。",
                            "proposal": prompt_hint or "明确双方在签约前已独立享有的背景知识产权仍各自保留所有权；转让范围仅限本次定制产出成果。",
                            "expected_text": txt,
                            "replacement_text": "除各方签约前已独立享有的既有知识产权（Background IP）及通用工具仍归原权利人所有外，" + txt
                        })

                # 1.4 交货迟延 / 逾期比例
                elif any(w in title for w in ["交货迟延", "迟延交付", "逾期比例", "交付期限", "供货违约"]):
                    candidates = find_best_blocks(["交货", "交付", "逾期", "迟延", "供货", "发货"], exclude_matched=True)
                    if candidates:
                        idx, b = candidates[0]
                        matched_block_indices.add(idx)
                        txt = b["text"]
                        cid = b["clause_id"]
                        findings.append({
                            "clause_id": cid,
                            "title": f"{title}：交货迟延违约金标准需设定合理起征宽限期与上限比例",
                            "severity": risk_level,
                            "evidence": txt,
                            "public_analysis": f"根据【{title}】规范：{prompt_hint or '逾期违约金每日按 0.1% 至 0.3% 计算，设置总上限'}。条款需规范迟延计算口径，防止因不可抗力或物流波动导致违约金畸高失衡。",
                            "proposal": "明确逾期交货每日违约金不超过未交付部分金额的千分之二，累计违约金总额不超过对应批次金额的 10%。",
                            "expected_text": txt,
                            "replacement_text": txt + "（迟延违约金每日按逾期未交部分货款金额的0.15%计算，单项累计违约金以迟延批次金额的10%为最高限额，并给予不少于3个工作日的不可归责宽限期）。"
                        })

                # 1.5 单方解除权限制与催告宽限期
                elif any(w in title for w in ["单方解除", "解除权", "催告宽限期", "随时解除", "终止合同"]):
                    candidates = find_best_blocks(["解除", "终止", "单方", "催告", "退换货", "随时"], exclude_matched=True)
                    if candidates:
                        idx, b = candidates[0]
                        matched_block_indices.add(idx)
                        txt = b["text"]
                        cid = b["clause_id"]
                        findings.append({
                            "clause_id": cid,
                            "title": f"{title}：合同单方解除权缺乏法定书面催告整改宽限保障",
                            "severity": risk_level,
                            "evidence": txt,
                            "public_analysis": f"审查清单【{title}】要求：主张解除合同须先行书面通知并在给予不少于15个工作日补救宽限期后方可行使。条款未明确书面催告流程，破坏合同严肃性与履约稳定性。",
                            "proposal": prompt_hint or "补充规定行使解除权前须给予对方不少于十五（15）个工作日的书面催告与补救整改宽限期。",
                            "expected_text": txt,
                            "replacement_text": txt + "（特别程序：任何一方依本条主张解除合同的，应提前十五（15）个工作日向对方送达书面催告函，对方在宽限期内完成整改消除违约后果的，合同应继续履行）。"
                        })

                # 1.6 争议管辖法院
                elif any(w in title for w in ["争议管辖", "管辖法院", "争议解决", "诉讼地"]):
                    candidates = find_best_blocks(["争议", "诉讼", "法院", "管辖", "协商不成", "仲裁"], exclude_matched=True)
                    if candidates:
                        idx, b = candidates[0]
                        matched_block_indices.add(idx)
                        txt = b["text"]
                        cid = b["clause_id"]
                        
                        target_mention = "对方所在地" if "对方所在地" in txt else ("原告" if "原告" in txt else "管辖法院")
                        findings.append({
                            "clause_id": cid,
                            "title": f"{title}：争议管辖法院应优选我方住所地或原告所在地人民法院",
                            "severity": risk_level,
                            "evidence": txt,
                            "public_analysis": f"依据【{title}】法务审查标准，争议管辖条款约定影响后续维权便利性。{prompt_hint or '防范异地诉讼高昂差旅与地方保护成本'}。建议约定为原告住所地或合同签订地人民法院管辖。",
                            "proposal": "修改为：由原告所在地或我方有管辖权的人民法院管辖。",
                            "expected_text": txt,
                            "replacement_text": re.sub(r'向.*人民法院提起诉讼', '向原告所在地或合同签订地有管辖权的人民法院提起诉讼', txt) if '人民法院' in txt else txt + "（争议发生协商不成的，应向原告住所地有管辖权的人民法院提起诉讼）。"
                        })

        # 2. General Fallback & Deep Legal Scanning on Unmatched Blocks
        for idx, b in enumerate(blocks):
            if idx in matched_block_indices:
                continue
            txt = b["text"]
            cid = b["clause_id"]

            # 违约赔偿责任未设定合理上限
            if "违约" in txt and ("全部损失" in txt or "不设上限" in txt or "赔偿全部" in txt or "无上限" in txt):
                matched_block_indices.add(idx)
                findings.append({
                    "clause_id": cid,
                    "title": "违约赔偿责任未设定合理上限与间接损失排除",
                    "severity": "high",
                    "evidence": txt,
                    "public_analysis": "条款约定赔偿全部直接与间接损失且未设赔偿限额，对我方构成不可预计的无限连带与重大经营风险。",
                    "proposal": "增加间接损失与商业利润损失排除条款，并将总赔偿责任限制在合同总金额的 100% 以内。",
                    "expected_text": txt,
                    "replacement_text": txt.replace("全部损失", "因本合同引起的直接经济损失（累计不超过本合同总价款金额，且不包括利润损失、商业信誉损失等间接损失）")
                })
            # 单方任意解除权与无宽限期
            elif "解除" in txt and ("随时解除" in txt or "无条件解除" in txt or "无需事先通知" in txt or "单方随时" in txt or "无需通知" in txt):
                matched_block_indices.add(idx)
                findings.append({
                    "clause_id": cid,
                    "title": "单方任意解除权失衡且缺乏合理宽限期",
                    "severity": "high",
                    "evidence": txt,
                    "public_analysis": "对方保留单方无条件随时解约权利，严重破坏履约确定性与交易稳定性，且未给予任何补救宽限期。",
                    "proposal": "增加至少 15 个工作日的书面催告整改期，逾期未改善方可触发解除。",
                    "expected_text": txt,
                    "replacement_text": txt + "（任何一方行使前述解除权前，应给予对方不少于十五（15）个工作日的书面催告与整改宽限期）。"
                })
            # 无限连带与连带保证
            elif "连带责任" in txt or "全部责任" in txt or "无限责任" in txt:
                matched_block_indices.add(idx)
                findings.append({
                    "clause_id": cid,
                    "title": "连带责任承担范围宽泛失衡",
                    "severity": "high",
                    "evidence": txt,
                    "public_analysis": "连带责任或不设限赔偿大幅超出过错相适应原则，可能导致我方承担超出实际受控范围的兜底风险。",
                    "proposal": "将连带责任修改为按各方实际过错程度承担相应按份赔偿责任。",
                    "expected_text": txt,
                    "replacement_text": txt.replace("连带责任", "与过错相适应的按份赔偿责任")
                })
            # 保密条款期限
            elif "商业秘密" in txt and ("永久" in txt or "无限期" in txt or "业务终止后" in txt):
                matched_block_indices.add(idx)
                findings.append({
                    "clause_id": cid,
                    "title": "商业秘密保护期与保密义务存续时限合理化",
                    "severity": "medium",
                    "evidence": txt,
                    "public_analysis": "保密期限约定过长将增加企业离职员工合规追溯及档案保管负担，建议设定为合理的两至三年期限（核心商业秘密除外）。",
                    "proposal": "明确常规商业秘密保护期为本协议终止后三（3）年内。",
                    "expected_text": txt,
                    "replacement_text": txt + "（双方确认：常规商务保密义务存续期为本协议履行期限届满或终止后三（3）年）。"
                })

        # 3. If no issues matched at all, provide high-value baseline check on first block
        if not findings and blocks:
            first_b = blocks[0]
            findings.append({
                "clause_id": first_b["clause_id"],
                "title": "合同首部签约主体资质合规与授权代表确认",
                "severity": "low",
                "evidence": first_b["text"],
                "public_analysis": "请核对各方营业执照有效存续状态、企业信用公示信息及法定代表人/授权委托人的合法签字授权文件有效性。",
                "proposal": "在合同末尾附件补充法定代表人身份证明书及法人授权委托书附卷备查。",
                "expected_text": first_b["text"],
                "replacement_text": first_b["text"] + "（附：双方主体资格及授权委托文件）"
            })

        return findings

model_gateway = ModelGateway()
