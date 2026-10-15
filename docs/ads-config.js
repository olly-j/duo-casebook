/* CB-002: owner-reviewed public configuration only. No credentials belong here. */
window.CASEBOOK_ADS_CONFIG = Object.freeze({
  enabled: false,
  publisherId: null,
  slots: Object.freeze({ catalogue: null, article: null }),
  publisherApproved: false,
  siteApproved: false,
  consentReady: false,
  approvedHosts: Object.freeze([]),
  consentConfigId: null,
  requiredPurposes: Object.freeze([1, 3, 4, 7, 9, 10])
});
