const globeContainer = document.getElementById("export-globe");

async function initializeExportGlobe() {
  if (!globeContainer || !window.Globe) return;
  let globe;
  try {
    const response = await fetch(globeContainer.dataset.mapUrl);
    if (!response.ok) throw new Error("세계 지도 자료를 불러오지 못했습니다.");
    const countries = await response.json();
    if (countries.type !== "FeatureCollection" || !countries.features?.length) {
      throw new Error("세계 지도 자료의 형식이 올바르지 않습니다.");
    }
    const locations = [
      { country: "KR", badge: "KR", lat: 37.5, lng: 127, name: "대한민국 (원산지)" },
      { country: "US", badge: "US", lat: 38, lng: -98 },
      { country: "EU", badge: "EU", lat: 48.5, lng: 10 },
      { country: "EAC", badge: "EAEU", lat: 55.8, lng: 50 },
      { country: "AE", badge: "UAE", lat: 25.2, lng: 55.3 },
    ];
    globe = new Globe(globeContainer, { animateIn: false, waitForGlobeReady: false })
      .backgroundColor("rgba(0,0,0,0)")
      .atmosphereColor("#b4a5e6")
      .atmosphereAltitude(0.14)
      .polygonsData(countries.features)
      .polygonCapColor(() => "rgba(220,214,244,0.90)")
      .polygonSideColor(() => "rgba(198,190,232,0.55)")
      .polygonStrokeColor(() => "rgba(172,162,215,0.75)")
      .polygonAltitude(0.007)
      .polygonsTransitionDuration(0)
      .pointsData(locations)
      .pointColor(d => d.country === "KR" ? "#6655a8" : "#9b8ec4")
      .pointAltitude(0.055)
      .pointRadius(d => d.country === "KR" ? 0.72 : 0.54)
      .htmlElementsData(locations)
      .htmlAltitude(0.09)
      .htmlElement(location => {
        const target = document.querySelector(`.export-fallback [data-country="${location.country}"]`);
        const marker = document.createElement(target ? "a" : "span");
        marker.className = `globe-marker${target ? "" : " globe-marker--origin"}`;
        if (location.country === "EU") marker.className += " globe-marker--eu";
        marker.textContent = location.badge;
        marker.title = target ? `${target.textContent.trim()} 성분 진단·로드맵 보기` : location.name;
        marker.setAttribute("aria-label", marker.title);
        if (target) marker.href = target.href;
        return marker;
      })
      .width(globeContainer.clientWidth)
      .height(globeContainer.clientHeight);

    // Reuse Globe.GL's material without adding a second Three.js dependency.
    const material = globe.globeMaterial();
    material.color.set("#fffefd");
    material.emissive.set("#eeeaf6");
    material.emissiveIntensity = 0.42;
    material.specular.set("#d8d0f0");
    material.shininess = 12;
    globe.controls().autoRotate = false;
    globe.controls().enableZoom = false;
    globe.controls().enablePan = false;
    globe.pointOfView({ lat: 22, lng: 115, altitude: 1.72 });
    globeContainer.classList.add("is-ready");
    new ResizeObserver(() => {
      globe.width(globeContainer.clientWidth).height(globeContainer.clientHeight);
    }).observe(globeContainer);
  } catch (error) {
    globe?.pauseAnimation();
    globeContainer.classList.remove("is-ready");
    globeContainer.replaceChildren();
    console.warn("지구본 대신 평면 지도와 권역 링크를 표시합니다.", error);
  }
}

initializeExportGlobe();
