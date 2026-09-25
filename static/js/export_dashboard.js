const globeContainer = document.getElementById("export-globe");
if (globeContainer && window.Globe) {
  try {
    const locations = [
      { country: "US", lat: 39, lng: -98 },
      { country: "EU", lat: 50, lng: 10 },
      { country: "EAC", lat: 55, lng: 75 },
      { country: "AE", lat: 24, lng: 54 },
    ];
    const globe = new Globe(globeContainer)
      .globeImageUrl(globeContainer.dataset.mapUrl)
      .backgroundColor("rgba(0,0,0,0)")
      .atmosphereColor("#c9c8f3")
      .atmosphereAltitude(0.13)
      .htmlElementsData(locations)
      .htmlAltitude(0.015)
      .htmlElement(location => {
        const target = document.querySelector(`.export-fallback [data-country="${location.country}"]`);
        const marker = document.createElement("a");
        marker.href = target.href;
        marker.className = "globe-marker";
        marker.setAttribute("aria-label", target.textContent.trim());
        marker.innerHTML = '<span class="globe-marker__tile"><svg viewBox="0 0 32 32" aria-hidden="true"><path d="M8 12h12c4 0 4-5 0-5-2 0-3 1-3 2M6 16h18c4 0 4 5 0 5-2 0-3-1-3-2M9 20h7c4 0 4 5 0 5-2 0-3-1-3-2" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></span><span class="globe-marker__ring"></span>';
        return marker;
      })
      .onGlobeReady(() => globeContainer.classList.add("is-ready"))
      .width(globeContainer.clientWidth)
      .height(globeContainer.clientHeight)
      .pointOfView({ lat: 42, lng: 63, altitude: 1.7 });
    new ResizeObserver(() => globe.width(globeContainer.clientWidth).height(globeContainer.clientHeight)).observe(globeContainer);
  } catch (error) {
    globeContainer.replaceChildren();
  }
}
