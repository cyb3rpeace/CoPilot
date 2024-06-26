<template>
	<div class="integrations-list">
		<div class="header mb-4 flex gap-2 justify-between items-center" v-if="!hideTotals">
			<div>
				Total:
				<strong class="font-mono">{{ totalIntegrations }}</strong>
			</div>
		</div>
		<n-spin :show="loadingIntegrations">
			<div class="list">
				<template v-if="integrationsList.length">
					<IntegrationItem
						v-for="integration of integrationsList"
						:key="integration.id"
						:integration="integration"
						:embedded="embedded"
						:selectable="isSelectable(integration)"
						:disabled="isDisabled(integration)"
						:checked="selectedIntegration?.id === integration.id"
						@click="setItem(integration)"
						class="item-appear item-appear-bottom item-appear-005 mb-2"
					/>
				</template>
				<template v-else>
					<n-empty description="No items found" class="justify-center h-48" v-if="!loadingIntegrations" />
				</template>
			</div>
		</n-spin>
	</div>
</template>

<script setup lang="ts">
import { ref, onBeforeMount, computed } from "vue"
import { useMessage, NSpin, NEmpty } from "naive-ui"
import Api from "@/api"
import IntegrationItem from "./IntegrationItem.vue"
import type { AvailableIntegration } from "@/types/integrations.d"

const { embedded, hideTotals, selectable, disabledIdsList } = defineProps<{
	embedded?: boolean
	hideTotals?: boolean
	selectable?: boolean
	disabledIdsList?: (string | number)[]
}>()

const selectedIntegration = defineModel<AvailableIntegration | null>("selected", { default: null })

const message = useMessage()
const loadingIntegrations = ref(false)
const integrationsList = ref<AvailableIntegration[]>([])

const totalIntegrations = computed<number>(() => {
	return integrationsList.value.length || 0
})

function isDisabled(integration: AvailableIntegration) {
	return (disabledIdsList || []).includes(integration.id)
}

function isSelectable(integration: AvailableIntegration) {
	return selectable && !isDisabled(integration)
}

function setItem(integration: AvailableIntegration) {
	if (!isDisabled(integration)) {
		selectedIntegration.value = selectedIntegration.value?.id === integration.id ? null : integration
	}
}

function getAvailableIntegrations() {
	loadingIntegrations.value = true

	Api.integrations
		.getAvailableIntegrations()
		.then(res => {
			if (res.data.success) {
				integrationsList.value = res.data?.available_integrations || []
			} else {
				message.warning(res.data?.message || "An error occurred. Please try again later.")
			}
		})
		.catch(err => {
			message.error(err.response?.data?.message || "An error occurred. Please try again later.")
		})
		.finally(() => {
			loadingIntegrations.value = false
		})
}

onBeforeMount(() => {
	getAvailableIntegrations()
})
</script>

<style lang="scss" scoped>
.integrations-list {
	.list {
		container-type: inline-size;
		min-height: 200px;
	}
}
</style>
