## 차선인식 프로젝트 시연영상
[수정 전 동영상][링크](https://drive.google.com/file/d/1MdOXBKet_ULtAm5qHkZOsc7WRfDcO9BY/view?usp=drive_link)

[수정 후 동영상][링크](https://drive.google.com/file/d/1PSVOEENlLh1I3kowVFXptJD6pj2GCnfm/view?usp=drive_link)
## 📊 프로젝트 개요
- **Bird-eye View 변환** (차선 영역을 더 잘 보이도록 투영 변환 적용)
- **Sobel Edge Detection 활용** (차선 경계를 강조)
- **Color Filtering & Masking 적용** (노란색, 흰색 차선을 강조)
- **조명 변화 보정 (CLAHE 적용)** (어두운 환경에서도 차선 검출 가능)
- **차선 검출 실패 시 예외 처리** (안정적인 검출 성능 유지)
- **실시간 차선 인식 & 결과 영상 저장**
## 📊 개발 과정 & 핵심 개념

### 🚀 **Birds-eye View 변환을 적용한 이유**
- 원근 효과 때문에 차선이 왜곡되는 문제를 해결하기 위해 적용  
- 투영 변환을 사용해 차선을 "수직 시점"에서 볼 수 있도록 변환  

### 🎯 **ROI(관심 영역)를 설정한 이유**
- 모든 도로 영역을 분석하면 불필요한 정보가 많아짐  
- 차량이 주행하는 주요 차선만 인식하도록 ROI를 수동 설정  

### 🛠 **차선 인식 성능 향상을 위한 조치**
- CLAHE 적용 → 밝기 변화에 강하도록 조정  
- Sobel Edge Detection → 노이즈를 줄이고 경계선 강조  
- 히스토리 기반 보정 → 차선이 끊겨도 예측 가능하도록 처리  

### ⚠️ **차선 검출이 실패하는 경우 & 해결법**
- 너무 밝거나 어두운 환경 → **CLAHE 적용**으로 해결  
- 노면이 지저분하거나 차선이 닳은 경우 → **히스토리 기반 예측 적용**  
- 카메라 왜곡 문제 → **calibration_data.p 적용, 새 영상에는 새 보정값 필요**  
