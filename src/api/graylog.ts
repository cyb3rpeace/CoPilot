import { HttpClient } from "./httpClient"
import type { FlaskBaseResponse } from "@/types/flask.d"
import {
	type Message,
	type ThroughputMetric,
	type IndexData,
	type Inputs,
	InputState,
	type Streams
} from "@/types/graylog.d" // Import Graylog interfaces

export default {
	getMessages(page?: number) {
		return HttpClient.get<FlaskBaseResponse & { graylog_messages: Message[]; total_messages: number }>(
			`/graylog/messages`,
			{
				params: {
					page_number: page || 1
				}
			}
		)
	},
	getMetrics() {
		return HttpClient.get<FlaskBaseResponse & { metrics: ThroughputMetric[] }>(`/graylog/metrics`)
	},
	getIndices() {
		return HttpClient.get<FlaskBaseResponse & { indexData: IndexData }>(`/graylog/indices`)
	},
	deleteIndex(indexName: string) {
		return HttpClient.delete<FlaskBaseResponse>(`/graylog/index`, {
			data: { index_name: indexName }
		})
	},
	getInputsRunning() {
		return HttpClient.get<FlaskBaseResponse & { inputs: Inputs }>(`/graylog/inputs/running`)
	},
	getInputsConfigured() {
		return HttpClient.get<FlaskBaseResponse & { inputs: Inputs }>(`/graylog/inputs/configured`)
	},
	startInput(inputId: string) {
		return HttpClient.put<FlaskBaseResponse>(`/graylog/inputs/${inputId}/start`)
	},
	stopInput(inputId: string) {
		return HttpClient.delete<FlaskBaseResponse>(`/graylog/inputs/${inputId}/stop`)
	},
	getInputState(inputId: string) {
		return HttpClient.get<FlaskBaseResponse & { state: InputState }>(`/graylog/inputs/${inputId}/state`)
	},
	getStreams() {
		return HttpClient.get<FlaskBaseResponse & { streams: Streams }>(`/graylog/streams`)
	},
	stopStream(streamId: string) {
		return HttpClient.post<FlaskBaseResponse>(`/graylog/streams/${streamId}/pause`)
	},
	startStream(streamId: string) {
		return HttpClient.post<FlaskBaseResponse>(`/graylog/streams/${streamId}/resume`)
	}
}
