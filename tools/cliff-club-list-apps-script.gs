// Receives Cliff Club invite list sign-ups from lp.oakcliffpilates.com/cliff-club
// and adds each one as a row in the "Cliff Club List Sign-ups" Google Sheet.
// Setup steps are in README.md under "Cliff Club invite list".

var SHEET_ID = '1hp-_Xs9iiST08QYspq-KrlQyHbxIS_jg0vPQSO6n464';
var TAB = 'Sign-ups';
var FIELDS = ['first_name', 'email', 'phone', 'instagram', 'who', 'source'];

function doPost(e) {
  var p = (e && e.parameter) || {};
  if (p.company) return reply({ ok: true }); // bot filled the hidden field
  if (!p.first_name || !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(p.email || '')) {
    return reply({ ok: false, error: 'missing name or email' });
  }

  var row = [new Date()].concat(FIELDS.map(function (k) { return clean(p[k]); }));
  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    SpreadsheetApp.openById(SHEET_ID).getSheetByName(TAB).appendRow(row);
  } finally {
    lock.releaseLock();
  }
  return reply({ ok: true });
}

// Keeps a typed value from running as a formula in the Sheet, and caps its length.
function clean(v) {
  v = String(v || '').trim().slice(0, 300);
  return /^[=+\-@]/.test(v) ? "'" + v : v;
}

function reply(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
