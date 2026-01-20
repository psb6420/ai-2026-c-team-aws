# ai-2026-c-team
# AWS Lambda + Amazon Bedrock (Claude Sonnet 4) API

이 프로젝트는 **AWS Lambda**를 통해 **Amazon Bedrock의 Claude Sonnet 4 모델**을 호출하고,
**API Gateway**를 통해 프론트엔드에서 쉽게 사용할 수 있는 **LLM API 엔드포인트**를 제공합니다.

---

## 🧩 아키텍처 개요

```
Frontend (Web / App)
        │
        ▼
API Gateway (HTTP API)
        │
        ▼
AWS Lambda (Python)
        │
        ▼
Amazon Bedrock
(Claude Sonnet 4)
```

* 프론트엔드에서 텍스트 요청 전송
* API Gateway가 Lambda 호출
* Lambda가 Bedrock Runtime을 통해 Claude 모델 호출
* 응답을 JSON 형태로 반환 (CORS 지원)

---

## ⚙️ 주요 기능

* ✅ Claude Sonnet 4 (`anthropic.claude-sonnet-4`) 호출
* ✅ 다양한 요청 필드(`prompt`, `message`, `input`, `text`) 자동 처리
* ✅ CORS 헤더 포함 (웹 프론트엔드 연동 가능)
* ✅ 오류 상황에 대한 HTTP 상태 코드 처리
* ✅ 환경 변수 기반 설정 (모델, 토큰 수, temperature)

---

## 📦 환경 변수 설정

Lambda 환경 변수로 다음 값을 설정할 수 있습니다.

| 변수명           | 설명            | 기본값                                       |
| ------------- | ------------- | ----------------------------------------- |
| `AWS_REGION`  | Bedrock 리전    | `us-east-1`                               |
| `MODEL_ID`    | Bedrock 모델 ID | `anthropic.claude-sonnet-4-20250514-v1:0` |
| `MAX_TOKENS`  | 최대 생성 토큰 수    | `512`                                     |
| `TEMPERATURE` | 응답 다양성        | `0.6`                                     |

---

## 🧠 Lambda 코드 설명

### 1. Bedrock 클라이언트 생성

```python
bedrock = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)
```

* Amazon Bedrock Runtime API를 사용해 Claude 모델을 호출합니다.

---

### 2. CORS 헤더 설정

```python
def _cors_headers():
```

* 모든 Origin(`*`)에서 접근 가능하도록 설정
* 브라우저 기반 프론트엔드 연동을 고려

---

### 3. 요청 데이터에서 프롬프트 추출

```python
def _extract_prompt(event):
```

다음 필드를 자동으로 인식합니다:

* `prompt`
* `message`
* `input`
* `text`
* `data` (JSON → 문자열 변환)

👉 프론트엔드 요청 형식이 달라도 유연하게 처리 가능

---

### 4. Claude 응답 파싱

```python
def _extract_answer(resp_body):
```

* Bedrock의 `content: [{type: "text"}]` 구조에서 텍스트만 추출
* 혹시 모를 다른 응답 포맷도 대비

---

### 5. Lambda 핸들러

```python
def lambda_handler(event, context):
```

처리 흐름:

1. `OPTIONS` 요청 → CORS Preflight 처리
2. 프롬프트 누락 시 `400 Bad Request`
3. Bedrock 모델 호출
4. 응답 파싱 후 JSON 반환
5. 예외 발생 시 `500 Internal Server Error`

---

## 📡 요청 예시

### HTTP POST

```json
{
  "prompt": "AWS Lambda에 대해 간단히 설명해줘"
}
```

---

## 📤 응답 예시

```json
{
  "answer": "AWS Lambda는 서버를 관리하지 않고 코드를 실행할 수 있는 서버리스 컴퓨팅 서비스입니다..."
}
```

---

## 🔐 IAM 권한 주의사항

Lambda 실행 역할(Role)에 다음 권한이 필요합니다.

```json
{
  "Effect": "Allow",
  "Action": [
    "bedrock:InvokeModel"
  ],
  "Resource": "*"
}
```

---

## 🚀 활용 예시

* AI 챗봇 백엔드
* 요약 / 번역 / 질문응답 API
* 프론트엔드 LLM 프록시 서버
* Claude 기반 서비스 PoC

---

## 📝 참고

* Amazon Bedrock는 **리전 제한**이 있으므로 모델 지원 여부 확인 필요
* API Gateway는 **HTTP API** 사용을 권장 (저렴 + CORS 간단)

---

필요하면

* **아키텍처 다이어그램 이미지용 설명**
* **프론트엔드 fetch 예제**
* **보안 강화 버전(API Key / Cognito)**
  까지 같이 정리해줄게.
