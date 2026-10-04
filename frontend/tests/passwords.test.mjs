import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import vm from 'node:vm'
import { validNewPassword } from '../src/utils/passwords.js'
import { authError } from '../src/utils/authErrors.js'

test('new password policy and UTF-8 limits match backend requirements', () => {
  for (const password of ['Short1!', 'lowercase1!', 'UPPERCASE1!', 'NoDigitsHere!', 'NoSpecial123', 'Spaces 123', 'Strong1!' + 'é'.repeat(33), 'NullChar1!\0']) {
    assert.equal(validNewPassword(password), false, password)
  }
  assert.ok(validNewPassword('Password1!'))
  assert.ok(validNewPassword(' Strong1!' + 'é'.repeat(31) + ' '))
  assert.ok(validNewPassword('Password1_'))
})

test('login errors distinguish wrong credentials, network, and backend outages', () => {
  assert.match(authError({ response: { status: 401 } }), /Invalid email or password/)
  assert.match(authError(new Error('network')), /Cannot reach the server/)
  for (const status of [500, 502, 503, 504]) {
    assert.match(authError({ response: { status, data: { detail: 'Internal error' } } }), /temporarily unavailable/)
  }
  assert.equal(authError({ response: { status: 422, data: { detail: [{ msg: 'Password too short' }] } } }), 'Password too short')
})

test('recovery entry removes token from URL before mounting and keeps it out of storage', async () => {
  const source = (await readFile(new URL('../src/recovery.js', import.meta.url), 'utf8')).replace(/^import .*$/gm, '')
  const actions = []
  const window = {
    location: { hash: '#token=private-test-token', pathname: '/reset-password' },
    history: { replaceState: (...args) => actions.push(['replace', ...args]) },
  }
  vm.runInNewContext(source, { window, URLSearchParams, PasswordRecoveryView: {},
    createApp: (_, props) => ({ mount: () => actions.push(['mount', props]) }) })
  assert.equal(actions[0][0], 'replace')
  assert.equal(actions[0][3], '/reset-password')
  assert.equal(actions[1][1].token, 'private-test-token')
  assert.equal(actions[1][1].resetting, true)
  const html = await readFile(new URL('../recovery.html', import.meta.url), 'utf8')
  assert.ok(!/https?:\/\//.test(html))
  assert.match(html, /name="referrer" content="no-referrer"/)
})
