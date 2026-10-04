import test from 'node:test'
import assert from 'node:assert/strict'
import { studentNavigation, exploreFeatures, isNavigationActive, subscriptionLabel } from '../src/utils/navigation.js'

test('five balanced destinations share Explore for dictionary and preserve core navigation', () => {
  assert.deepEqual(studentNavigation.map(x => x.to), ['/dashboard','/courses','/leaderboard','/explore','/profile'])
  assert.equal(studentNavigation[3].icon, 'explore')
  assert.ok(isNavigationActive('/dictionary','/explore'))
  assert.equal(exploreFeatures.find(x => x.name === 'Dictionary').to, '/dictionary')
  assert.ok(exploreFeatures.filter(x => x.name !== 'Dictionary').every(x => !x.to))
})

test('subscription wording reflects existing entitlement without inventing a higher tier', () => {
  assert.equal(subscriptionLabel({is_premium:true}), 'Manage subscription')
  assert.equal(subscriptionLabel({is_premium:false}), 'Go Premium')
})
