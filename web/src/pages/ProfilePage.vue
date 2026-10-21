<script setup>
import { onMounted, ref } from "vue";

const props = defineProps({
  me: { type: Object, required: true },
  err: { type: String, default: "" },
  errAt: { type: String, default: "" },
  savePassword: { type: Function, required: true },
  loadFailLibrary: { type: Function, required: true },
  resetFailLibrary: { type: Function, required: true },
  showErr: { type: Function, required: true },
});

const currentPwd = ref("");
const nextPwd = ref("");
const againPwd = ref("");
const pwdNote = ref("");
const failCount = ref(0);
const failQq = ref("");
const failNote = ref("");
const failBusy = ref(false);
const failReady = ref(false);

async function loadFail() {
  const data = await props.loadFailLibrary();
  failCount.value = Number(data.count) || 0;
  failQq.value = data.qq || "";
  failReady.value = true;
}

async function resetFail() {
  failNote.value = "";
  props.showErr("", "fail");
  if (!failQq.value) {
    props.showErr("还没有攻打 QQ，没有战败库", "fail");
    return;
  }
  const who = failCount.value ? `目前记了 ${failCount.value} 人。` : "";
  if (!window.confirm(`清空这个攻打号的战败库？${who}以前打不过的人会重新可以打。`)) return;
  failBusy.value = true;
  try {
    const data = await props.resetFailLibrary();
    const n = Number(data.removed) || 0;
    failNote.value = n ? `已清空 ${n} 人` : "战败库已经是空的";
    await loadFail();
  } finally {
    failBusy.value = false;
  }
}

onMounted(() => {
  loadFail().catch((e) => props.showErr(e.message, "fail"));
});

async function submitPwd() {
  pwdNote.value = "";
  props.showErr("", "pwd");
  if (nextPwd.value !== againPwd.value) {
    props.showErr("两次输入的新密码不一样", "pwd");
    return;
  }
  await props.savePassword(currentPwd.value, nextPwd.value);
  currentPwd.value = "";
  nextPwd.value = "";
  againPwd.value = "";
  pwdNote.value = "已修改";
}
</script>

<template>
  <section>
    <h2>个人中心</h2>
    <p>
      {{ me.username }} · {{ me.tier || "初级" }}<template v-if="me.expires_at"> · 有效期至 {{ me.expires_at }}</template>
    </p>
    <p>区服：<template v-if="me.region">{{ me.region }}区</template><template v-else>还没识别</template></p>
    <p class="muted">攻打号登录游戏后，从游戏链接里自动识别。目前只有 1 区支持订阅敌方。</p>
    <p>最近 1 天被超级强攻 {{ me.storm_day ?? 0 }} 次</p>
    <h3>修改密码</h3>
    <form class="stack" @submit.prevent="submitPwd().catch((e) => showErr(e.message, 'pwd'))">
      <label>当前密码
        <input v-model="currentPwd" type="password" autocomplete="current-password" required />
      </label>
      <label>新密码
        <input v-model="nextPwd" type="password" autocomplete="new-password" required />
      </label>
      <label>再输入一次
        <input v-model="againPwd" type="password" autocomplete="new-password" required />
      </label>
      <button type="submit">修改</button>
      <span v-if="pwdNote" class="muted">{{ pwdNote }}</span>
      <span v-if="err && errAt === 'pwd'" class="err">{{ err }}</span>
    </form>
    <p class="muted">改完之后这次登录还在。别处登录的要重新登录。</p>
    <h3>战败库</h3>
    <p class="muted">打不过的人记在这个攻打号上。清城和绕路都会避开他们。实力涨上来之后清空，就可以再打一遍。同一个攻打 QQ 绑了几个登录账号，用的是同一份。</p>
    <p v-if="!failReady" class="muted">正在看战败库。</p>
    <p v-else-if="failQq">目前记了 {{ failCount }} 人。</p>
    <p v-else class="muted">还没有攻打 QQ，没有战败库。</p>
    <p>
      <button type="button" :disabled="!failQq || failBusy" @click="resetFail().catch((e) => showErr(e.message, 'fail'))">重置战败库</button>
      <span v-if="failNote" class="muted">{{ failNote }}</span>
      <span v-if="err && errAt === 'fail'" class="err">{{ err }}</span>
    </p>
  </section>
</template>
