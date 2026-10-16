<script setup>
const count = defineModel("count", { type: String, required: true });
const aaCount = defineModel("aaCount", { type: String, required: true });

defineProps({
  dailyQq: { type: String, default: "" },
  jobs: { type: Array, required: true },
  blast: { default: null },
  note: { type: String, default: "" },
  err: { type: String, default: "" },
  errAt: { type: String, default: "" },
  runBlast: { type: Function, required: true },
  runAa: { type: Function, required: true },
  cancelJob: { type: Function, required: true },
  showErr: { type: Function, required: true },
});
</script>

<template>
  <section>
    <h2>基地战</h2>
    <p v-if="dailyQq">攻打 QQ {{ dailyQq }}</p>
    <p v-else class="muted">还没绑定攻打 QQ。按页面上方的步骤点登录并扫码。一个登录账号只绑一个攻打号，这里的制造用那个号做。</p>
    <p class="muted">由这个账号的攻打线程执行，不另开连接。正在打的那一单会先打完，然后做这项。</p>
    <h2>兵营</h2>
    <p>当前爆破兵 {{ blast === null || blast === undefined ? "还没读到" : blast }}</p>
    <form class="lock-row" @submit.prevent="runBlast(count).catch((e) => showErr(e.message))">
      <span class="switch">爆破兵制造</span>
      <label>数量<input v-model="count" class="mins" inputmode="numeric" required /></label>
      <button type="submit" :disabled="!dailyQq">开始制造</button>
    </form>
    <p class="muted">按这个数量循环。每次先生产一个，剩余时间算出 0 勋章才快速制造，credit 固定写 0。要花勋章就停在这一只，不发。大厅蓝钻大约要等剩余降到 600 秒，一只一分多钟。消耗金属和石油。数量 1 到 399。兵营里已经在造的那一只算进数量。</p>
    <h2>战车工厂</h2>
    <form class="lock-row" @submit.prevent="runAa(aaCount).catch((e) => showErr(e.message))">
      <span class="switch">防空车制造</span>
      <label>数量<input v-model="aaCount" class="mins" inputmode="numeric" required /></label>
      <button type="submit" :disabled="!dailyQq">开始制造</button>
    </form>
    <p class="muted">按这个数量循环造防空车。每次先开工，剩余时间算出 0 勋章才快速制造，credit 固定写 0。大厅蓝钻剩余降到 600 秒以内才发。要花勋章就停在这一辆，不发。工厂里已经在造防空车的那一辆算进数量，正在造别的就不打断。消耗金属和石油。数量 1 到 399。</p>
    <p v-if="note" class="muted">{{ note }}</p>
    <p v-if="err && errAt === 'base'" class="err">{{ err }}</p>
    <h2>最近执行</h2>
    <p v-if="!jobs.length" class="muted">还没有执行记录。</p>
    <div v-else class="wide">
      <table class="daily-jobs">
        <thead>
          <tr><th>项目</th><th>状态</th><th>说明</th><th>北京时间</th></tr>
        </thead>
        <tbody>
          <tr v-for="it in jobs" :key="it.id">
            <td>{{ it.label }}</td>
            <td>{{ it.status }}<button v-if="it.status === '排队' || it.status === '正在做'" type="button" class="ghost" @click="cancelJob(it).catch((e) => showErr(e.message))">关停</button></td>
            <td class="reason">{{ it.detail || "—" }}</td>
            <td>{{ it.created_at || "—" }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
