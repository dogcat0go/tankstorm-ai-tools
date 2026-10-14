<script setup>
const count = defineModel("count", { type: String, required: true });

defineProps({
  dailyQq: { type: String, default: "" },
  jobs: { type: Array, required: true },
  blast: { default: null },
  metal: { default: null },
  oil: { default: null },
  credit: { default: null },
  note: { type: String, default: "" },
  err: { type: String, default: "" },
  errAt: { type: String, default: "" },
  runBlast: { type: Function, required: true },
  cancelJob: { type: Function, required: true },
  showErr: { type: Function, required: true },
});

function resText(n) {
  if (n === null || n === undefined || n === "") return "还没读到";
  const num = Number(n);
  if (!Number.isFinite(num)) return "还没读到";
  return Math.trunc(num).toLocaleString("zh-CN");
}
</script>

<template>
  <section>
    <h2>基地战</h2>
    <p v-if="dailyQq">攻打 QQ {{ dailyQq }}</p>
    <p v-else class="muted">还没绑定攻打 QQ。按页面上方的步骤点登录并扫码。一个登录账号只绑一个攻打号，这里的制造用那个号做。</p>
    <p class="muted">由这个账号的攻打线程执行，不另开连接。正在打的那一单会先打完，然后做这项。</p>
    <h2>基地内资源</h2>
    <p>金属 {{ resText(metal) }} · 石油 {{ resText(oil) }}</p>
    <p>勋章 {{ resText(credit) }}</p>
    <p class="muted">每 10 秒从攻打号已经收到的资源里更新一次。不另向游戏要一份。还没收到就显示还没读到。</p>
    <h2>兵营</h2>
    <p>当前爆破兵 {{ blast === null || blast === undefined ? "还没读到" : blast }}</p>
    <form class="lock-row" @submit.prevent="runBlast(count).catch((e) => showErr(e.message))">
      <span class="switch">爆破兵制造</span>
      <label>数量<input v-model="count" class="mins" inputmode="numeric" required /></label>
      <button type="submit" :disabled="!dailyQq">开始制造</button>
    </form>
    <p class="muted">按这个数量循环。每次先生产一个，剩余时间算出 0 勋章才快速制造，credit 固定写 0。要花勋章就停在这一只，不发。大厅蓝钻大约要等剩余降到 600 秒，一只一分多钟。消耗金属和石油。数量 1 到 399。兵营里已经在造的那一只算进数量。</p>
    <h2>战场工厂</h2>
    <p class="muted">还没有制造项。</p>
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
