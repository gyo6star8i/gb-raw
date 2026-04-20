#!/usr/bin/env python3
"""
경상북도교육청 업무 법령 관계도 - 법령 질의응답 서버
Claude API를 활용하여 교육공무원 관련 법령 질문에 답변합니다.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, origins=[
    "https://gyo6star8i.github.io",
    "http://localhost:*",
    "http://127.0.0.1:*"
])

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# 법령 맵의 노드 정보 (컨텍스트용)
LAW_CONTEXT = """
당신은 경상북도교육청 교육공무원 업무 법령 전문 안내 챗봇입니다.
아래 법령 목록을 바탕으로 질문에 답변하고, 반드시 근거 법령을 명시해주세요.

=== 핵심 법령 ===
- 교육공무원법: 교육공무원 자격·임용·보수·연수·신분보장·징계 등 기본법
- 국가공무원법: 교육공무원에 규정 없는 사항 준용
- 교원의 지위 향상 및 교육활동 보호를 위한 특별법(교원지위법): 교원 지위 향상, 교육활동 보호

=== 임용·자격·승진 ===
- 교육공무원임용령: 임용, 전보, 파견, 복직 등 세부 절차
- 교육공무원승진규정: 승진 심사 기준, 경력·연수·공적 평점
- 교육공무원인사위원회규정: 인사위원회 구성·운영
- 교원자격검정령 및 시행규칙: 교원 자격 취득 기준
- 교사임용후보자명부작성규칙: 임용 후보자 명부 작성
- 수석교사재심사에관한규칙: 수석교사 재심사 절차
- 공무원임용령: 임용 일반 절차
- 공무원채용신체검사규정: 채용 신체검사 절차
- 교육공무원인사관리규정(예규): 인사기록 작성·유지
- 교장·원장임기제실시업무처리지침(예규): 교장·원장 임기제

=== 복무·연수 ===
- 국가공무원복무규정: 복무 의무, 근무시간, 각종 휴가 기준
- 국가공무원복무·징계관련예규(인사혁신처): 복무·징계 실무 종합
- 교원연수규정(교원 등의 연수에 관한 규정): 연수 종류, 연수기관
- 교원연수규정시행규칙: 연수기관 지정 세부 절차
- 교원연수이수실적의기록및관리요령(예규): 연수 이수실적 관리
- 교원휴가에관한예규: 교원 연가·병가·공가·특별휴가 기준

=== 징계·비위 ===
- 교육공무원징계령: 징계 절차, 징계위원회 구성·운영, 감경 기준
- 교육공무원징계양정등에관한규칙: 비위 유형별 징계 기준, 감경 사유
- 공무원징계령: 징계 절차 일반 규정
- 공무원비위사건처리규정(예규): 비위사건 보고·처리 절차

=== 소청·교권 ===
- 교원소청에관한규정: 소청심사 청구 절차
- 교원지위법시행령: 소청심사위원회 구성, 교육활동 침해 처리

=== 보수·연금 ===
- 공무원보수규정: 봉급·수당 등 보수 체계
- 공무원연금법: 퇴직·장해·사망 급여
- 국가공무원명예퇴직수당등지급규정(명예퇴직수당지급규정): 명예퇴직 수당
- 교원명예퇴직수당지급에관한특례규정(예규): 교원 명예퇴직 수당 특례
- 교육공무원호봉획정시경력환산율표의적용등에관한예규: 호봉확정 경력 환산
- 기간제교원의봉급지급에관한예규: 기간제 교원 봉급

=== 학생보호 ===
- 학교폭력예방 및 대책에 관한 법률(학교폭력예방법): 학교폭력 예방·대책
- 아동복지법: 아동학대 신고의무
- 교원의학생생활지도에관한고시: 학생 생활지도 기준
- 스토킹범죄의처벌등에관한법률(스토킹처벌법): 스토킹범죄 피해 보호

=== 지방교육자치·계약 ===
- 지방교육자치에관한법률(지방교육자치법): 교육감 선출, 교육청 조직
- 지방자치단체를당사자로하는계약에관한법률(지방계약법): 계약 체결 절차
- 지방자치단체입찰및계약집행기준(예규): 입찰·낙찰 실무 집행기준

=== 경상북도 지역 법령 ===
- 경북교육청행정기구설치조례: 경북교육청 행정조직·직제·정원
- 경북교육감행정권한위임조례 및 규칙: 권한 위임 기준
- 경북도립학교관리·운영규칙: 도립학교 관리·운영
- 경북교원직무수행심의위원회규칙: 직무수행 심의
- 경북교육청교권보호위원회규칙: 교권보호위원회 운영
- 경북공립학교회계규칙: 학교 회계 예산·집행·결산
- 교육공무원인사기록및인사사무처리규칙: 인사기록 작성·보관
- 교육감소속지방공무원인사기록규칙: 지방공무원 인사기록
- 교육공무원질병휴직위원회구성및운영예규: 질병휴직 심사
- 경북교육감소속공무국외출장규정: 국외출장 절차

=== 상훈·정보공개 ===
- 상훈법 및 시행령: 훈장·포장 수여 기준
- 공공기관의정보공개에관한법률(정보공개법): 정보공개 청구·불복

답변 형식:
1. 질문에 대한 명확한 답변 (핵심 내용 먼저)
2. 근거 법령 및 조문 명시
3. 주의사항 또는 예외가 있으면 추가 안내
4. 마지막에 JSON 형식으로 관련 법령 ID와 근거 조항 목록 제공:
   RELATED_LAWS: [{"id":"법령ID1","article":"제X조 제X항"},{"id":"법령ID2","article":"제X조"}]
   - article은 반드시 실제 근거 조항(예: "제20조의4", "제4조 제2항")으로 명시
   - 조항을 특정하기 어려운 경우 ""(빈 문자열)로 설정

법령 ID 목록 (JSON에 사용):
teacher_vacation, conduct_decree, civil_conduct_guide, edu_official, nation_official,
appoint_decree, promo_decree, hr_committee, qual_decree, training_decree, training_rule,
training_record, edu_punish, civil_punish, punish_standard, misconduct_proc,
appeal_decree, status_decree, pay_decree, pension_law, retire_pay, retire_special,
salary_calc, parttime_pay, school_violence, child_welfare, student_guide, stalking_law,
local_edu_auto, local_contract, gb_org_ord, gb_auth_ord, gb_auth_rule, gb_school_rule,
gb_duty_comm, gb_edu_protect, gb_school_account, gb_hr_record, gb_local_record,
gb_sick_leave, gb_abroad, award_law, info_law, health_check, hr_manage, principal_term,
cert_addendum, civil_conduct_guide
"""


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "law-chat"})


@app.route("/ask-law", methods=["POST"])
def ask_law():
    try:
        body = request.get_json(force=True)
        question = body.get("question", "").strip()

        if not question:
            return jsonify({"error": "질문을 입력해주세요."}), 400

        if len(question) > 500:
            return jsonify({"error": "질문이 너무 깁니다. 500자 이내로 입력해주세요."}), 400

        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1024,
            system=LAW_CONTEXT,
            messages=[
                {"role": "user", "content": question}
            ]
        )

        answer_text = message.content[0].text

        # RELATED_LAWS JSON 파싱
        related_laws = []
        if "RELATED_LAWS:" in answer_text:
            try:
                import json, re
                match = re.search(r'RELATED_LAWS:\s*(\[.*?\])', answer_text, re.DOTALL)
                if match:
                    raw = json.loads(match.group(1))
                    # 구형 string 배열도 호환 처리
                    for item in raw:
                        if isinstance(item, str):
                            related_laws.append({"id": item, "article": ""})
                        elif isinstance(item, dict):
                            related_laws.append({
                                "id": item.get("id", ""),
                                "article": item.get("article", "")
                            })
                    # 답변에서 RELATED_LAWS 줄 제거
                    answer_text = answer_text[:answer_text.find("RELATED_LAWS:")].strip()
            except Exception:
                pass

        return jsonify({
            "answer": answer_text,
            "related_laws": related_laws
        })

    except anthropic.APIError as e:
        return jsonify({"error": f"API 오류: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"서버 오류: {str(e)}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False)
