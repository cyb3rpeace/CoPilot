import { type FlaskBaseResponse } from "@/types/flask.d"
import { HttpClient } from "./httpClient"
import type {
	CheckoutPayload,
	License,
	LicenseCheckoutSession,
	LicenseFeatures,
	LicenseKey,
	SubscriptionFeature
} from "@/types/license.d"

export interface NewLicensePayload {
	name: string
	email: string
	companyName: string
}

export default {
	getLicense() {
		return HttpClient.get<FlaskBaseResponse & { license_key: LicenseKey }>(`/license/get_license`)
	},
	getSubscriptionFeatures() {
		return HttpClient.get<FlaskBaseResponse & { features: SubscriptionFeature[] }>(`/license/subscription_features`)
	},
	verifyLicense() {
		return HttpClient.get<FlaskBaseResponse & { license: License }>(`/license/verify_license`)
	},
	getLicenseFeatures() {
		return HttpClient.get<FlaskBaseResponse & { features: LicenseFeatures[] }>(`/license/get_license_features`)
	},
	replaceLicense(license_key: LicenseKey) {
		return HttpClient.post<FlaskBaseResponse>(`/license/replace_license_in_db`, {
			license_key
		})
	},
	createCheckoutSession(payload: CheckoutPayload) {
		return HttpClient.post<FlaskBaseResponse & { session: LicenseCheckoutSession }>(
			`/license/create_checkout_session`,
			payload
		)
	},
	retrieveLicenseByEmail(email: string) {
		return HttpClient.post<FlaskBaseResponse & { license_key: LicenseKey }>(`/license/retrieve_license_by_email`, {
			email
		})
	},
	// TODO: remove, deprecated
	extendLicense(period: number) {
		return HttpClient.post<FlaskBaseResponse>(
			`/license/extend_license`,
			{},
			{
				params: { period }
			}
		)
	},
	// TODO: remove, deprecated
	createLicense({ name, email, companyName }: NewLicensePayload) {
		return HttpClient.post<FlaskBaseResponse>(`/license/create_new_key`, {
			product_id: 24355,
			notes: "Test Key",
			new_customer: true,
			name,
			email,
			company_name: companyName
		})
	}
}
