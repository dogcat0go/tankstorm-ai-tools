<script setup>
import { computed } from "vue";
import { ElSwitch } from "element-plus";
import "element-plus/es/components/switch/style/css";

const guildLevel = defineModel("guildLevel", { type: String, required: true });
const fundBuilding = defineModel("fundBuilding", { type: String, required: true });
const fundTimes = defineModel("fundTimes", { type: String, required: true });

const props = defineProps({
  dailyQq: { type: String, default: "" },
  tasks: { type: Array, required: true },
  dailySwitching: { type: String, default: "" },
  note: { type: String, default: "" },
  fundBuildings: { type: Array, required: true },
  fundNote: { type: String, default: "" },
  err: { type: String, default: "" },
  errAt: { type: String, default: "" },
  saveLevel: { type: Function, required: true },
  saveDailySwitch: { type: Function, required: true },
  runFund: { type: Function, required: true },
  showErr: { type: Function, required: true },
});

const guildTask = computed(() => props.tasks.find((it) => it.key === "公会战役") || null);
</script>

<template>
  <section>
    <h2>活动助手</h2>
    <p v-if="dailyQq">攻打 QQ {{ dailyQq }}</p>
    <p v-else class="muted">还没绑定攻打 QQ。按页面上方的步骤点登录并扫码。一个登录账号只绑一个攻打号，这里的活动用那个号做。</p>
    <p class="muted">由这个账号的攻打线程执行，不另开连接。开关和日常任务是同一个。</p>
    <details class="campaign-box">
      <summary>公会战役</summary>
      <div v-if="guildTask" class="campaign-line">
        <span class="switch">{{ guildTask.name }}</span>
        <span class="campaign-ops">
          <el-switch
            class="daily-switch"
            size="large"
            inline-prompt
            active-text="开"
            inactive-text="关"
            :model-value="guildTask.on"
            :loading="dailySwitching === guildTask.key"
            :disabled="guildTask.locked"
            @change="saveDailySwitch(guildTask, $event)"
          />
          <span v-if="guildTask.locked" class="muted">功能尚在恢复中...</span>
        </span>
      </div>
      <form class="lock-row" @submit.prevent="saveLevel().catch((e) => showErr(e.message))">
        <span class="switch">攻打等级</span>
        <label>等级<input v-model="guildLevel" class="mins" inputmode="numeric" required /></label>
        <button type="submit">保存</button>
      </form>
      <p v-if="note" class="muted">{{ note }}</p>
      <p class="muted">只在周五 10:00 到周六 22:00（本机时间）执行。同一等级按体力一直打，直到体力不够、体力不再下降或被拒绝。能读到体力 thew，当前积分 nowPersonMsg.point。不领奖。等级记在这个登录账号上，没改过就用配置里的等级。保存后，下次进攻按这个等级打。</p>
    </details>
    <details class="campaign-box">
      <summary>成就拨款</summary>
      <form class="lock-row" @submit.prevent="runFund(fundBuilding, fundTimes).catch((e) => showErr(e.message))">
        <span class="switch">成就拨款</span>
        <label>建筑
          <select v-model="fundBuilding" class="fund-building" required>
            <option value="" disabled>选择建筑</option>
            <option v-for="b in fundBuildings" :key="b.id" :value="b.id">{{ b.name }}</option>
          </select>
        </label>
        <label>次数<input v-model="fundTimes" class="mins" inputmode="numeric" required /></label>
        <button type="submit">拨款</button>
      </form>
      <p v-if="fundNote" class="muted">{{ fundNote }}</p>
      <p class="muted">每次拨款前各开 4 张 1000 万金属卡和石油卡。次数 1 到 999。</p>
    </details>
    <p v-if="err && errAt === 'activity'" class="err">{{ err }}</p>
  </section>
</template>
