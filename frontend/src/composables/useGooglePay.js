import { loadScript } from '@/utils/loadScript'
const baseRequest = { apiVersion: 2, apiVersionMinor: 0 }
const card = { type: 'CARD', parameters: { allowedAuthMethods: ['PAN_ONLY', 'CRYPTOGRAM_3DS'], allowedCardNetworks: ['VISA', 'MASTERCARD'] } }
let client
let clientEnvironment

export function useGooglePay() {
  const environment = import.meta.env.VITE_GOOGLE_PAY_ENVIRONMENT || 'TEST'
  function getClient() {
    if (!window.google?.payments?.api) throw new Error('Google Pay is still loading. Please try again.')
    if (!['TEST', 'PRODUCTION'].includes(environment)) throw new Error('Google Pay environment is invalid.')
    if (!client || clientEnvironment !== environment) {
      client = new window.google.payments.api.PaymentsClient({ environment })
      clientEnvironment = environment
    }
    return client
  }
  async function isReady() {
    try {
      if (environment === 'PRODUCTION' && (!import.meta.env.VITE_GOOGLE_PAY_MERCHANT_ID || !import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY)) return false
      await loadScript('https://pay.google.com/gp/p/js/pay.js')
      return !!(await getClient().isReadyToPay({ ...baseRequest, allowedPaymentMethods: [card] })).result
    } catch { return false }
  }
  function requestPayment(amountKES, tierLabel) {
    const gateway = environment === 'TEST'
      ? { gateway: 'example', gatewayMerchantId: 'exampleGatewayMerchantId' }
      : { gateway: 'stripe', 'stripe:version': '2018-10-31', 'stripe:publishableKey': import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY }
    const merchantInfo = { merchantName: 'Vernaculearn' }
    if (import.meta.env.VITE_GOOGLE_PAY_MERCHANT_ID) merchantInfo.merchantId = import.meta.env.VITE_GOOGLE_PAY_MERCHANT_ID
    // Call synchronously within the click handler to retain browser user activation.
    return getClient().loadPaymentData({
      ...baseRequest,
      allowedPaymentMethods: [{ ...card, tokenizationSpecification: { type: 'PAYMENT_GATEWAY', parameters: gateway } }],
      merchantInfo,
      transactionInfo: { totalPriceStatus: 'FINAL', totalPrice: Number(amountKES).toFixed(2), currencyCode: 'KES', countryCode: 'KE', totalPriceLabel: tierLabel },
    }).then(data => data.paymentMethodData.tokenizationData.token)
  }
  function createButton(onClick) {
    return getClient().createButton({ onClick, buttonColor: 'black', buttonType: 'subscribe', buttonSizeMode: 'fill' })
  }
  return { isReady, requestPayment, createButton }
}
