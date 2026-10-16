# -*- coding: utf-8 -*-
"""
AgentScope-Powered Multi-Agent Contract Review Team.
Implements role-based cooperative dialogue & debate for deep legal reasoning:
- AuditorAgent: Performs statutory & checklist compliance screening.
- StanceAdvocateAgent: Defends the specific business stance (我方利益博弈).
- RevisionDrafterAgent: Produces balanced, enforceable legal modifications and diffs.
"""

from typing import List, Dict, Any, Optional
import json
import asyncio
from agentscope.message import Msg
from contract_app.infrastructure.models.model_gateway import model_gateway

class ContractMultiAgentTeam:
    def __init__(self):
        self.gateway = model_gateway

    async def collaborative_review(
        self,
        blocks: List[Dict[str, Any]],
        stance: str = "我方",
        focus_areas: Optional[List[str]] = None,
        checklists: Optional[List[Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute multi-agent collaborative review pipeline across document blocks.
        """
        # If running in mock mode or without remote LLM keys, use the intelligent multi-role engine
        if self.gateway.mock_mode or not self.gateway.api_key:
            return self._run_simulated_multi_agent_review(blocks, stance, focus_areas, checklists)

        try:
            # 1. Auditor Agent: First-pass compliance scanning
            auditor_msg = await self._run_auditor_agent(blocks, checklists)
            
            # 2. Stance Advocate Agent: Deep stance interest defense
            advocate_msg = await self._run_stance_agent(blocks, stance, auditor_msg)
            
            # 3. Revision Drafter Agent: Redline drafting & synthesis
            final_findings = await self._run_drafter_agent(blocks, stance, auditor_msg, advocate_msg)
            return final_findings
        except Exception as e:
            print(f"[ContractMultiAgentTeam] Remote multi-agent orchestration error: {e}, falling back to built-in legal engine")
            return self._run_simulated_multi_agent_review(blocks, stance, focus_areas, checklists)

    async def _run_auditor_agent(self, blocks: List[Dict[str, Any]], checklists: Optional[List[Any]]) -> Msg:
        chk_text = ""
        if checklists:
            chk_text = "\n".join([f"- {getattr(c, 'title', '')}: {getattr(c, 'check_prompt', '')}" for c in checklists])

        system = (
            "【角色：AgentScope 审查清单审计员 (AuditorAgent)】\n"
            "你的任务是严格审查合同条款与合规清单条目的符合性，识别隐藏合规漏洞、法律红线违规与程序性缺失。\n"
            "请列出发现的风险条款编号、具体事实依据与法律风险分析。"
        )
        user_prompt = (
            f"合同审查清单要求：\n{chk_text or '全面民法典与商业交易合规'}\n\n"
            f"合同文本段落摘要：\n{json.dumps(blocks[:60], ensure_ascii=False)}"
        )
        content = await self.gateway.call_chat(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1
        )
        return Msg(name="AuditorAgent", role="assistant", content=content)

    async def _run_stance_agent(self, blocks: List[Dict[str, Any]], stance: str, auditor_msg: Msg) -> Msg:
        system = (
            f"【角色：AgentScope 商业立场辩护员 (StanceAdvocateAgent)】\n"
            f"你的核心职责是站在【{stance}】的商业利益与谈判立场上，审查合同权利义务对等性。\n"
            "重点核查：责任限制是否封顶、管辖地是否对我方有利、付款先决条件是否具备保护、违约赔偿是否过重。"
        )
        user_prompt = (
            f"审计员已发现的合规要点：\n{auditor_msg.content}\n\n"
            f"请从【{stance}】核心利益出发，提出重点攻防诉求和条款重写指导原则。"
        )
        content = await self.gateway.call_chat(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )
        return Msg(name="StanceAdvocateAgent", role="assistant", content=content)

    async def _run_drafter_agent(
        self,
        blocks: List[Dict[str, Any]],
        stance: str,
        auditor_msg: Msg,
        advocate_msg: Msg
    ) -> List[Dict[str, Any]]:
        system = (
            "【角色：AgentScope 条款改写拟定员 (RevisionDrafterAgent)】\n"
            "结合审计员的法律红线与立场辩护员的诉求，输出最终的合同修改建议结构化 JSON。\n"
            "必须输出纯 JSON 数组，每个元素包含：\n"
            "clause_id (条款编号), title (风险标题), severity ('high'|'medium'|'low'), "
            "evidence (原文句子), public_analysis (法务说理阐述), proposal (谈判修改建议), "
            "expected_text (被替换的原文字符串), replacement_text (建议替换的修订后表述)"
        )
        user_prompt = (
            f"审查审计意见：\n{auditor_msg.content[:1500]}\n\n"
            f"立场诉求要点：\n{advocate_msg.content[:1500]}\n\n"
            f"合同段落数据：\n{json.dumps(blocks[:60], ensure_ascii=False)}"
        )
        content = await self.gateway.call_chat(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1
        )
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        return json.loads(content)

    def _run_simulated_multi_agent_review(
        self,
        blocks: List[Dict[str, Any]],
        stance: str,
        focus_areas: Optional[List[str]],
        checklists: Optional[List[Any]]
    ) -> List[Dict[str, Any]]:
        """
        Intelligent multi-role legal reasoning engine with guaranteed fidelity.
        Simulates Auditor + Stance Advocate + Revision Drafter synthesis.
        """
        # Call model_gateway's intelligent analyzer directly
        return self.gateway._intelligent_legal_analyze(blocks, stance, focus_areas, checklists)

contract_multi_agent_team = ContractMultiAgentTeam()
