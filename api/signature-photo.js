// POST /api/signature-photo
// Saves a new email-signature photo to the site.
//
// The page sends { person, image, key }: `image` is a base64 JPEG (data URL or raw),
// already cropped to a square in the browser. The photo is committed to the repo as
// signatures/img/{person}-{timestamp}.jpg and signatures/photos.json is pointed at it,
// in one commit on main. Vercel redeploys on that push, so the photo goes live at
// https://lp.oakcliffpilates.com/signatures/img/... in about a minute.
//
// Earlier photos stay in the repo on purpose: emails already sent keep loading them.
//
// Vercel env vars (Project > Settings > Environment Variables, Production):
//   SIGNATURE_UPLOAD_KEY  the passcode people type on the page
//   GITHUB_TOKEN          fine-grained token, this repo only, Contents: Read and write

const crypto = require('crypto');

const REPO = 'kijacreative/ocp-landing-pages';
const BRANCH = 'main';
const PEOPLE = ['kiel', 'isabel', 'charley', 'stephanie', 'amanda', 'ocp'];
const MAX_BYTES = 1024 * 1024; // the page sends about 40 KB

function sameKey(a, b) {
  const ha = crypto.createHash('sha256').update(String(a)).digest();
  const hb = crypto.createHash('sha256').update(String(b)).digest();
  return crypto.timingSafeEqual(ha, hb);
}

async function gh(path, options = {}) {
  const res = await fetch(`https://api.github.com/repos/${REPO}${path}`, {
    ...options,
    headers: {
      Authorization: `Bearer ${process.env.GITHUB_TOKEN}`,
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
      'User-Agent': 'ocp-signature-photo',
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
    },
  });
  if (!res.ok) {
    const text = await res.text();
    const err = new Error(`GitHub ${res.status} on ${path}: ${text.slice(0, 300)}`);
    err.status = res.status;
    throw err;
  }
  return res.json();
}

async function commitPhoto(person, bytes) {
  const stamp = new Date().toISOString().replace(/[-:]/g, '').replace(/\..+/, '').replace('T', '-');
  const imagePath = `signatures/img/${person}-${stamp}.jpg`;

  const ref = await gh(`/git/ref/heads/${BRANCH}`);
  const headSha = ref.object.sha;
  const head = await gh(`/git/commits/${headSha}`);

  let photos = {};
  try {
    const file = await gh(`/contents/signatures/photos.json?ref=${headSha}`);
    photos = JSON.parse(Buffer.from(file.content, 'base64').toString('utf8'));
  } catch (e) {
    if (e.status !== 404) throw e;
  }
  photos[person] = imagePath.replace('signatures/', '');

  const blob = await gh('/git/blobs', {
    method: 'POST',
    body: JSON.stringify({ content: bytes.toString('base64'), encoding: 'base64' }),
  });
  const tree = await gh('/git/trees', {
    method: 'POST',
    body: JSON.stringify({
      base_tree: head.tree.sha,
      tree: [
        { path: imagePath, mode: '100644', type: 'blob', sha: blob.sha },
        { path: 'signatures/photos.json', mode: '100644', type: 'blob', content: JSON.stringify(photos, null, 2) + '\n' },
      ],
    }),
  });
  const commit = await gh('/git/commits', {
    method: 'POST',
    body: JSON.stringify({
      message: `Signatures: new photo for ${person}`,
      tree: tree.sha,
      parents: [headSha],
    }),
  });
  // Not forced: if main moved in the meantime this fails and the page asks to try again.
  await gh(`/git/refs/heads/${BRANCH}`, {
    method: 'PATCH',
    body: JSON.stringify({ sha: commit.sha, force: false }),
  });
  return { path: photos[person], photos };
}

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ error: 'Use POST.' });
  }
  if (!process.env.SIGNATURE_UPLOAD_KEY || !process.env.GITHUB_TOKEN) {
    return res.status(503).json({ error: 'Photo saving is not set up yet. See the README, "Email signatures".' });
  }

  let body = req.body;
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch { body = null; }
  }
  const { person, image, key } = body || {};

  if (!key || !sameKey(key, process.env.SIGNATURE_UPLOAD_KEY)) {
    return res.status(401).json({ error: 'That passcode is not right.' });
  }
  if (!PEOPLE.includes(person)) {
    return res.status(400).json({ error: 'Unknown signature.' });
  }
  if (typeof image !== 'string') {
    return res.status(400).json({ error: 'No photo was sent.' });
  }
  const bytes = Buffer.from(image.replace(/^data:image\/jpeg;base64,/, ''), 'base64');
  const isJpeg = bytes.length > 3 && bytes[0] === 0xff && bytes[1] === 0xd8 && bytes[2] === 0xff;
  if (!isJpeg || bytes.length > MAX_BYTES) {
    return res.status(400).json({ error: 'The photo must be a JPEG under 1 MB.' });
  }

  try {
    const saved = await commitPhoto(person, bytes);
    return res.status(200).json({ ok: true, ...saved });
  } catch (e) {
    console.error(e);
    const busy = e.status === 422;
    return res.status(busy ? 409 : 502).json({
      error: busy ? 'Someone else saved at the same moment. Try again.' : 'Could not save the photo. Try again in a minute.',
    });
  }
};
