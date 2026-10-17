// File: help.js | Path: nms-help/help.js | Purpose: offline topic filtering and printing.
// filterTopics: show matching sidebar topics without network requests or stored data.
function filterTopics() {
  const query = document.querySelector('#topic-filter').value.trim().toLowerCase(); // Read the current query.
  const topics = [...document.querySelectorAll('[data-topic]')]; // Collect local navigation items.
  topics.forEach(item => { item.hidden = !item.textContent.toLowerCase().includes(query); }); // Filter labels.
  document.querySelector('#no-topics').hidden = topics.some(item => !item.hidden); // Explain empty results.
}
document.querySelector('#topic-filter').addEventListener('input', filterTopics); // Filter as the visitor types.
document.querySelector('#print-page').addEventListener('click', () => window.print()); // Use browser printing.
