<template>
	<div class="page">
		<div class="flex wrapper justify-center" v-if="!isLogged">
			<div class="image-box basis-2/3" v-if="align === 'right'"></div>
			<div class="form-box basis-1/3 flex items-center justify-center" :class="{ centered: align === 'center' }">
				<AuthForm :type="type" />
			</div>
			<div class="image-box basis-2/3" v-if="align === 'left'">
				<video playsinline autoplay muted loop poster="/images/login/cover.webp">
					<source src="/images/login/video.mp4" type="video/mp4" />
					Your browser does not support the video tag.
				</video>
			</div>
		</div>
	</div>
</template>

<script lang="ts" setup>
import AuthForm from "@/components/auth/AuthForm.vue"
import { ref, computed, onBeforeMount, toRefs } from "vue"
import { useRoute } from "vue-router"
import { useThemeStore } from "@/stores/theme"
import { useAuthStore } from "@/stores/auth"
import type { FormType } from "@/components/auth/types.d"

type Align = "left" | "center" | "right"

const props = defineProps<{
	formType?: FormType
}>()
const { formType } = toRefs(props)

const route = useRoute()
const align = ref<Align>("left")
const activeColor = ref("")
const type = ref<FormType | undefined>(formType.value || undefined)

const primaryColor = computed(() => useThemeStore().primaryColor)
const isLogged = computed(() => useAuthStore().isLogged)

onBeforeMount(() => {
	if (route.query.step) {
		const step = route.query.step as FormType
		type.value = step
	}
	activeColor.value = primaryColor.value
})
</script>

<style lang="scss" scoped>
@import "@/assets/scss/common.scss";

.page {
	min-height: 100vh;

	.settings {
		position: fixed;
		top: 10px;
		left: 50%;
		transform: translateX(-50%);
		background-color: var(--bg-secondary-color);
		height: 44px;
		width: 300px;
		border-radius: 50px;
		padding: 5px;
		z-index: 1;
	}

	.wrapper {
		min-height: 100vh;

		.image-box {
			background-color: v-bind(activeColor);
			position: relative;

			video {
				position: absolute;
				top: 0;
				left: 0;
				width: 100%;
				height: 100%;
				object-fit: cover;
				object-position: center;
			}

			/*
			&::after {
				content: "";
				width: 100%;
				height: 100%;
				position: absolute;
				top: 0;
				left: 0;
				background-image: url(@/assets/images/pattern-onboard.png);
				background-size: 500px;
				background-position: center center;
			}
			*/
		}

		.form-box {
			padding: 50px;

			&.centered {
				flex-basis: 100%;
				.form-wrap {
					padding: 60px;
					width: 100%;
					max-width: 500px;
					background-color: var(--bg-color);
					border-radius: 20px;
					@apply shadow-xl;
				}

				@media (max-width: 600px) {
					padding: 4%;
					.form-wrap {
						padding: 8%;
					}
				}
			}
		}
	}
	@media (max-width: 800px) {
		.settings {
			width: 112px;
			.colors {
				display: none;
			}
		}
		.wrapper {
			.image-box {
				display: none;
			}

			.form-box {
				flex-basis: 100%;
			}
		}
	}
}
</style>
