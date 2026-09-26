// Run: node test_export_globe.cjs (no browser or extra dependencies).
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('static/js/export_dashboard.js', 'utf8');

async function check(mode) {
  const classes = new Set();
  const markers = [];
  const regions = { US: 'us', EU: 'eu', EAC: 'eac', AE: 'uae' };
  const container = {
    dataset: { mapUrl: '/map.json' }, clientWidth: 800, clientHeight: 480,
    classList: { add: x => classes.add(x), remove: x => classes.delete(x) },
    replaceChildren() { this.cleared = true; },
  };
  const material = { color: { set() {} }, emissive: { set() {} }, specular: { set() {} } };
  let locations;
  const api = new Proxy({}, { get: (_, key) => {
    if (key === 'htmlElementsData') return value => { locations = value; return api; };
    if (key === 'htmlElement') return value => { markers.push(...locations.map(value)); return api; };
    if (key === 'globeMaterial') return () => material;
    if (key === 'controls') return () => ({});
    return () => api;
  } });
  const context = {
    window: { Globe: mode !== 'cdn' },
    document: {
      getElementById: () => container,
      querySelector: selector => {
        const country = selector.match(/data-country="(.*?)"/)[1];
        return regions[country] && { href: `/dashboard?region=${regions[country]}`, textContent: country };
      },
      createElement: tag => ({ tag, setAttribute() {} }),
    },
    fetch: async () => ({ ok: mode !== 'http', json: async () => mode === 'invalid' ? {} : { type: 'FeatureCollection', features: [{}] } }),
    Globe: function () { if (mode === 'webgl') throw new Error('WebGL unavailable'); return api; },
    ResizeObserver: class { observe() {} }, console: { warn() {} },
  };
  await vm.runInNewContext(source, context);
  assert.equal(classes.has('is-ready'), mode === 'ok');
  if (mode === 'ok') {
    assert.equal(markers.length, 5);
    assert.equal(markers.find(m => m.textContent === 'KR').tag, 'span');
    assert.deepEqual(markers.filter(m => m.tag === 'a').map(m => m.href).sort(),
      Object.values(regions).map(r => `/dashboard?region=${r}`).sort());
  } else if (mode !== 'cdn') assert.equal(container.cleared, true);
}
(async () => {
  for (const mode of ['ok', 'cdn', 'http', 'invalid', 'webgl']) await check(mode);
  console.log('Globe links and failure fallback: PASS');
})().catch(error => { console.error(error); process.exitCode = 1; });
