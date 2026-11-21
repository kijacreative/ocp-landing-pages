// Receives Shop Small with OCP sign-ups from lp.oakcliffpilates.com/smallbusinesssaturday.
// For each one it adds a row to this Sheet, saves the logo and photo to a Drive folder,
// emails Isabel every field with links to both files, and emails the business a confirmation.
//
// Setup, once (also in README.md under "Shop Small sign-ups"):
// 1. Make a new Google Sheet named "Shop Small 2026 Sign-ups". Extensions > Apps Script.
// 2. Replace the editor contents with this file and save.
// 3. Pick "setup" in the function menu and Run it. Approve the access prompt.
//    It makes the "Sign-ups" tab and the "Shop Small 2026 uploads" Drive folder,
//    and shares the Sheet and folder with Isabel.
// 4. Deploy > New deployment > Web app. Execute as: Me. Who has access: Anyone. Deploy.
// 5. Copy the web app URL (ends in /exec) into SBS_FORM_ENDPOINT in smallbusinesssaturday/index.html and deploy the site.
// After editing this script, use Deploy > Manage deployments > Edit > New version so the URL stays the same.

var NOTIFY = 'isabel@oakcliffpilates.com';
var TAB = 'Sign-ups';
var FOLDER_NAME = 'Shop Small 2026 uploads';
// 12:00 AM Central, Thursday, Nov 26, 2026. Anything after this is turned away.
var DEADLINE = new Date('2026-11-26T00:00:00-06:00');
var MB = 1024 * 1024;

var COLUMNS = [
  ['submitted_at', 'Submitted (Dallas time)'],
  ['business_name', 'Business name'],
  ['first_name', 'First name'],
  ['last_name', 'Last name'],
  ['email', 'Email'],
  ['phone', 'Phone'],
  ['website', 'Website'],
  ['instagram', 'Instagram'],
  ['address', 'Address'],
  ['neighborhood', 'Neighborhood'],
  ['category', 'Category'],
  ['relationship', 'How they know OCP'],
  ['offer_headline', 'Offer headline'],
  ['offer_details', 'Offer details'],
  ['promo_code', 'Promo code'],
  ['redeem', 'Where to redeem'],
  ['valid', 'Offer valid'],
  ['about', 'One line about the business'],
  ['honor', 'Will honor offer'],
  ['consent', 'OK to use logo, photo, offer'],
  ['logo_url', 'Logo file'],
  ['photo_url', 'Photo file'],
  ['source', 'Source']
];

var REQUIRED = ['business_name', 'first_name', 'last_name', 'email', 'instagram', 'neighborhood', 'category',
  'relationship', 'offer_headline', 'offer_details', 'redeem', 'valid'];
var MAX_LEN = { offer_headline: 60, offer_details: 200, about: 120 };
var UPLOADS = {
  logo: { types: { 'image/png': 'png', 'image/svg+xml': 'svg', 'image/jpeg': 'jpg' }, max: 10 * MB },
  photo: { types: { 'image/png': 'png', 'image/jpeg': 'jpg' }, max: 15 * MB }
};

function setup() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(TAB) || ss.insertSheet(TAB, 0);
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(COLUMNS.map(function (c) { return c[1]; }));
    sheet.setFrozenRows(1);
    sheet.getRange(1, 1, 1, COLUMNS.length).setFontWeight('bold');
  }
  var folder = getFolder();
  try { ss.addEditor(NOTIFY); } catch (err) { Logger.log('Share the Sheet with ' + NOTIFY + ' by hand: ' + err); }
  try { folder.addEditor(NOTIFY); } catch (err) { Logger.log('Share the folder with ' + NOTIFY + ' by hand: ' + err); }
  Logger.log('Sheet: ' + ss.getUrl());
  Logger.log('Uploads folder: ' + folder.getUrl());
}

function doPost(e) {
  var p;
  try { p = JSON.parse((e && e.postData && e.postData.contents) || '{}'); } catch (err) { return json({ ok: false, error: 'bad request' }); }
  if (p.company) return json({ ok: true }); // honeypot: bots fill the hidden field
  if (new Date() >= DEADLINE) return json({ ok: false, error: 'closed' });

  var f = {};
  COLUMNS.forEach(function (c) { f[c[0]] = String(p[c[0]] || '').trim(); });
  f.instagram = f.instagram.replace(/^@+/, '');
  for (var i = 0; i < REQUIRED.length; i++) if (!f[REQUIRED[i]]) return json({ ok: false, error: 'missing ' + REQUIRED[i] });
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(f.email)) return json({ ok: false, error: 'bad email' });
  for (var k in MAX_LEN) if (f[k].length > MAX_LEN[k]) return json({ ok: false, error: k + ' too long' });
  if (p.honor !== 'Yes' || p.consent !== 'Yes') return json({ ok: false, error: 'missing confirmations' });

  var blobs = {};
  for (var key in UPLOADS) {
    var u = p[key] || {};
    var extn = UPLOADS[key].types[u.type];
    if (!extn || !u.data) return json({ ok: false, error: 'bad ' + key });
    var bytes = Utilities.base64Decode(u.data);
    if (bytes.length > UPLOADS[key].max) return json({ ok: false, error: key + ' too big' });
    blobs[key] = { bytes: bytes, type: u.type, ext: extn };
  }

  var lock = LockService.getScriptLock();
  lock.waitLock(30000);
  try {
    var folder = getFolder();
    var slug = slugify(f.business_name);
    var base = uniqueBase(folder, slug, blobs);
    var files = {};
    for (var name in blobs) {
      var b = blobs[name];
      files[name] = folder.createFile(Utilities.newBlob(b.bytes, b.type, base + '-' + name + '.' + b.ext));
    }
    f.logo_url = files.logo.getUrl();
    f.photo_url = files.photo.getUrl();
    f.submitted_at = Utilities.formatDate(new Date(), 'America/Chicago', 'yyyy-MM-dd HH:mm:ss');
    f.source = f.source || 'lp.oakcliffpilates.com/smallbusinesssaturday';
    f.honor = 'Yes';
    f.consent = 'Yes';

    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(TAB);
    sheet.appendRow(COLUMNS.map(function (c) { return clean(f[c[0]]); }));
  } finally {
    lock.releaseLock();
  }

  notifyIsabel(f);
  confirmBusiness(f);
  return json({ ok: true });
}

function notifyIsabel(f) {
  var lines = COLUMNS.map(function (c) { return c[1] + ': ' + (f[c[0]] || '(blank)'); });
  try {
    MailApp.sendEmail({
      to: NOTIFY,
      replyTo: f.email,
      subject: 'Shop Small sign-up: ' + f.business_name,
      body: lines.join('\n') + '\n\nAll sign-ups: ' + SpreadsheetApp.getActiveSpreadsheet().getUrl()
    });
  } catch (err) { Logger.log('Notify failed: ' + err); }
}

function confirmBusiness(f) {
  try {
    MailApp.sendEmail({
      to: f.email,
      replyTo: NOTIFY,
      name: 'Oak Cliff Pilates',
      subject: "You're in for Small Business Saturday",
      body: 'Thanks, ' + f.first_name + '. ' + f.business_name + ' is in. Your feature goes out Friday, Nov 27 in our email and on @oakcliffpilates. Questions or changes: ' + NOTIFY + '.'
    });
  } catch (err) { Logger.log('Confirmation failed: ' + err); }
}

function getFolder() {
  var props = PropertiesService.getScriptProperties();
  var id = props.getProperty('FOLDER_ID');
  if (id) { try { return DriveApp.getFolderById(id); } catch (err) {} }
  var folder = DriveApp.createFolder(FOLDER_NAME);
  props.setProperty('FOLDER_ID', folder.getId());
  return folder;
}

// "{slug}" unless a file with that name is already there, then "{slug}-2", "{slug}-3"...
function uniqueBase(folder, slug, blobs) {
  for (var n = 1; n < 100; n++) {
    var base = n === 1 ? slug : slug + '-' + n;
    var taken = Object.keys(blobs).some(function (k) {
      return folder.getFilesByName(base + '-' + k + '.' + blobs[k].ext).hasNext();
    });
    if (!taken) return base;
  }
  return slug + '-' + Date.now();
}

function slugify(s) {
  return String(s).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()
    .replace(/&/g, ' and ').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 60) || 'business';
}

// Keep values short and stop them being read as spreadsheet formulas.
function clean(v) {
  v = String(v || '').trim().slice(0, 500);
  return /^[=+\-@]/.test(v) ? "'" + v : v;
}

function json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
