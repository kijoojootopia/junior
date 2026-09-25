// 대시보드 프론트 스크립트
document.addEventListener("DOMContentLoaded", () => {
    const uploadForm = document.getElementById("uploadForm");
    const resultTableBody = document.getElementById("screeningResults");
    const statusBadge = document.getElementById("screenStatus");

    if (!uploadForm) return;

    const regionSelect = document.getElementById("regionSelect");
    const requestedRegion = new URLSearchParams(window.location.search).get("region");
    if ([...regionSelect.options].some(option => option.value === requestedRegion)) {
        regionSelect.value = requestedRegion;
    }
    const pipelineTypeSelect = document.getElementById("pipelineTypeSelect");
    const pipelineTypeControl = document.getElementById("pipeline-type-control");
    const pipelineLabel = document.getElementById("pipeline-label");
    const pipelinePanels = document.querySelectorAll(".document-pipeline-panel");

    function updatePipeline() {
        const isUS = regionSelect.value === "us";
        const productType = isUS ? pipelineTypeSelect.value : "GENERAL";
        pipelineTypeControl.hidden = !isUS;
        pipelinePanels.forEach(panel => {
            panel.hidden = panel.dataset.region !== regionSelect.value
                || panel.dataset.productType !== productType;
        });
        pipelineLabel.textContent = regionSelect.selectedOptions[0].textContent
            + (isUS ? ` · ${pipelineTypeSelect.selectedOptions[0].textContent}` : "");
    }

    regionSelect.addEventListener("change", updatePipeline);
    pipelineTypeSelect.addEventListener("change", updatePipeline);
    updatePipeline();

    uploadForm.addEventListener("submit", async (e) => {
        // 1. 브라우저 기본 페이지 새로고침 차단
        e.preventDefault();

        const fileInput = document.getElementById("csvFile");

        if (!fileInput.files || fileInput.files.length === 0) {
            alert("CSV 파일을 선택해주세요.");
            return;
        }

        // 2. 백엔드로 전달할 Form 데이터 구성
        const formData = new FormData();
        formData.append("file", fileInput.files[0]);
        formData.append("region", regionSelect.value);

        // 3. UI 분석 중 상태 표시
        if (statusBadge) {
            statusBadge.textContent = "진단 분석 중...";
            statusBadge.style.background = "#f39c12";
            statusBadge.style.color = "#ffffff";
        }
        resultTableBody.innerHTML = `<tr><td colspan="5" class="placeholder-text">데이터를 정밀 분석하고 있습니다. 잠시만 기다려주세요...</td></tr>`;

        try {
            // 4. Flask 백엔드 /api/screen 라우터로 전송
            const response = await fetch("/api/screen", {
                method: "POST",
                body: formData,
            });

            const data = await response.json();

            if (!response.ok || data.error) {
                alert(data.error || "분석 중 오류가 발생했습니다.");
                if (statusBadge) {
                    statusBadge.textContent = "오류 발생";
                    statusBadge.style.background = "#e74c3c";
                    statusBadge.style.color = "#ffffff";
                }
                return;
            }

            // 5. 검사 결과 테이블 렌더링
            renderResults(data.result);

            if (statusBadge) {
                statusBadge.textContent = "진단 완료";
                statusBadge.style.background = "#2ecc71";
                statusBadge.style.color = "#ffffff";
            }

        } catch (error) {
            console.error("Screening Error:", error);
            alert("서버 통신 중 에러가 발생했습니다.");
            if (statusBadge) {
                statusBadge.textContent = "통신 에러";
                statusBadge.style.background = "#e74c3c";
                statusBadge.style.color = "#ffffff";
            }
        }
    });

    // 진단 결과 테이블 행 생성 함수
    function renderResults(results) {
        if (!results || results.length === 0) {
            resultTableBody.innerHTML = `<tr><td colspan="5" class="placeholder-text">분석된 성분 결과가 없습니다.</td></tr>`;
            return;
        }

        let html = "";
        results.forEach((item) => {
            const isViolation = item.is_violation;
            
            // 배합 금지 및 한도 초과 시 붉은색 강조, 정상일 때 녹색
            const badgeColor = isViolation ? "#e74c3c" : "#2ecc71";
            const badgeText = isViolation ? "위험 / 위반" : "통과 (Pass)";
            const statusTextColor = isViolation ? "#c0392b" : "#2c3e50";
            
            // 상세 사유(conditions) 및 법령 근거(source) 결합
            let detailText = item.conditions || "규제 세부 규정 확인 필요";
            if (item.source) {
                detailText += ` <span style="display: inline-block; margin-left: 4px; color: #7f8c8d; font-size: 11px;">[${item.source}]</span>`;
            }

            // 위반 성분인 경우 행 전체에 연한 붉은색 배경 적용
            const rowStyle = isViolation 
                ? "background-color: #fdf2f2; border-left: 4px solid #e74c3c;" 
                : "";

            html += `
                <tr style="${rowStyle}">
                    <td><strong>${item.inci_name}</strong></td>
                    <td>${item.concentration}%</td>
                    <td><span style="font-weight: 600; color: ${statusTextColor};">${item.status}</span></td>
                    <td><span style="color: ${badgeColor}; font-weight: bold;">${badgeText}</span></td>
                    <td style="font-size: 13px; line-height: 1.45; color: ${isViolation ? '#c0392b' : '#555'};">
                        ${detailText}
                    </td>
                </tr>
            `;
        });

        resultTableBody.innerHTML = html;
    }
});
