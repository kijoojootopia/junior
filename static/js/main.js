// 대시보드 프론트 스크립트
document.addEventListener("DOMContentLoaded", () => {
    const uploadForm = document.getElementById("uploadForm");
    const resultTableBody = document.getElementById("screeningResults");
    const statusBadge = document.getElementById("screenStatus");

    if (!uploadForm) return;

    uploadForm.addEventListener("submit", async (e) => {
        // 1. 브라우저의 기본 새로고침 동작 차단
        e.preventDefault();

        const fileInput = document.getElementById("csvFile");
        const regionSelect = document.getElementById("regionSelect");

        if (!fileInput.files || fileInput.files.length === 0) {
            alert("CSV 파일을 선택해주세요.");
            return;
        }

        // 2. FormData 객체 생성
        const formData = new FormData();
        formData.append("file", fileInput.files[0]);
        formData.append("region", regionSelect.value);

        // UI 상태 업데이트
        statusBadge.textContent = "진단 분석 중...";
        statusBadge.style.background = "#f39c12";
        resultTableBody.innerHTML = `<tr><td colspan="5" class="placeholder-text">데이터를 분석하고 있습니다. 잠시만 기다려주세요...</td></tr>`;

        try {
            // 3. Flask 서버의 /api/screen 라우터로 비동기 요청 전송
            const response = await fetch("/api/screen", {
                method: "POST",
                body: formData,
            });

            const data = await response.json();

            if (!response.ok || data.error) {
                alert(data.error || "분석 중 오류가 발생했습니다.");
                statusBadge.textContent = "오류 발생";
                statusBadge.style.background = "#e74c3c";
                return;
            }

            // 4. 결과 테이블 렌더링
            renderResults(data.result);
            statusBadge.textContent = "진단 완료";
            statusBadge.style.background = "#2ecc71";

        } catch (error) {
            console.error("Screening Error:", error);
            alert("서버 통신 중 에러가 발생했습니다.");
            statusBadge.textContent = "통신 에러";
            statusBadge.style.background = "#e74c3c";
        }
    });

    // 테이블 행 동적 생성 함수
    function renderResults(results) {
        if (!results || results.length === 0) {
            resultTableBody.innerHTML = `<tr><td colspan="5" class="placeholder-text">분석된 성분 결과가 없습니다.</td></tr>`;
            return;
        }

        let html = "";
        results.forEach((item) => {
            const isDanger = item.is_violation;
            const badgeColor = isDanger ? "#e74c3c" : "#2ecc71";
            const badgeText = isDanger ? "위험/주의" : "통과 (Pass)";
            const statusLabel = item.status === "PROHIBITED" ? "배합 금지" : (item.status === "RESTRICTED" ? "배합 한도" : "미해당");

            html += `
                <tr>
                    <td><strong>${item.inci_name}</strong></td>
                    <td>${item.concentration}%</td>
                    <td>${statusLabel}</td>
                    <td><span style="color: ${badgeColor}; font-weight: bold;">${badgeText}</span></td>
                    <td style="font-size: 12px; color: #555;">${item.conditions || item.source}</td>
                </tr>
            `;
        });

        resultTableBody.innerHTML = html;
    }
});