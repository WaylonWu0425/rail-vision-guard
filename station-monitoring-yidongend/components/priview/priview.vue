<template>
	<view>
		<view class="cards-list">
				<view v-for="(item,index) in computedData" class="card" :style="`background-color:${color[index]||''}`">
					<view class="value">
						<uv-image :src="`../../static/homeIcon/${item.type}.png`" width="36px" height="38px"></uv-image>
						<!-- <uv-icon color="#fff" :size="38"  name="heart"></uv-icon> -->
						<text>{{item.value.toFixed()}}</text>
					</view>
					<view class="footer">
						<view class="label">
							{{item.title}}
						</view>
						<view class="unit">
							{{item.unit}}
						</view>
					</view>
				</view>
		</view>
	</view>
</template>

<script setup>
	import { useEnvironmentStore } from '../../store/environmentData';
import { computed, ref } from 'vue';
let environmentStore = useEnvironmentStore()
let computedData = computed(()=>{
	return environmentStore.sensorData.filter(selectData)
})

function selectData(item){
	return item.type === 'breath'||item.type==='heart'||item.type==='distance'|| item.type==='move'
}
let color = [
	'#5BCEBD',
	null,
	'#FF724B',
	'#FB1374'
]

</script>

<style lang="scss">
	.cards-list{
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 10px 10px;
	}
		.card {
			box-sizing: border-box;
			padding: 12px;
			background-color: $color-primary;
			position: relative;
			border-radius: 12px;
			color: #fff;

			.value {
				font-size: 28px;
				width: 100%;
				display: flex;
				justify-content: space-between;
			}

			.footer {
				display: flex;
				justify-content: space-between;
				align-items: end;
				padding: 0 4px;
				.unit {
					font-size: 13px;
					color: #fff
				}

				.label {
					font-size: 13px;
				}
			}
		}
	
</style>