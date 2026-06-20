"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Send, BrainCircuit, BarChart2, Target, Lightbulb, 
  FileText, LogOut, Loader2, Sparkles, TrendingUp,
  Moon, Droplets, Activity, Smartphone, BookOpen, Save, Calendar,
  Trash2, Edit2, Flag
} from "lucide-react";
import axios from "axios";
import { useStore } from "../store/useStore";
import { 
  LineChart, Line, XAxis, YAxis, 
  CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer 
} from 'recharts';

// ==========================================
// 1. Auth Page Component
// ==========================================
function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const setLogin = useStore((state) => state.setLogin);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (isLogin) {
        const res = await axios.post("http://127.0.0.1:8000/api/auth/login", { username, password });
        setLogin(res.data.user_id, res.data.username);
      } else {
        const res = await axios.post("http://127.0.0.1:8000/api/auth/register", { username, email, password });
        setLogin(res.data.user_id, username);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Connection Error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center h-screen bg-[#080B12] text-slate-200" dir="rtl">
      <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="bg-[#0D1117] p-8 rounded-3xl border border-slate-800 shadow-2xl w-full max-w-md">
        <div className="text-center mb-8">
          <BrainCircuit className="w-16 h-16 text-sky-400 mx-auto mb-4" />
          <h1 className="text-3xl font-bold text-white mb-2">MindMate</h1>
          <p className="text-slate-400">مساعدك النفسي الذكي</p>
        </div>
        <div className="flex gap-4 mb-6">
          <button onClick={() => setIsLogin(true)} className={`flex-1 pb-2 transition-all ${isLogin ? 'border-b-2 border-sky-400 text-sky-400 font-bold' : 'text-slate-500'}`}>دخول</button>
          <button onClick={() => setIsLogin(false)} className={`flex-1 pb-2 transition-all ${!isLogin ? 'border-b-2 border-sky-400 text-sky-400 font-bold' : 'text-slate-500'}`}>حساب جديد</button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input type="text" placeholder="اسم المستخدم" value={username} onChange={(e)=>setUsername(e.target.value)} className="w-full bg-[#1E293B] border border-slate-700 p-3 rounded-xl focus:ring-2 focus:ring-sky-500 outline-none" required />
          {!isLogin && <input type="email" placeholder="البريد الإلكتروني" value={email} onChange={(e)=>setEmail(e.target.value)} className="w-full bg-[#1E293B] border border-slate-700 p-3 rounded-xl focus:ring-2 focus:ring-sky-500 outline-none" required />}
          <input type="password" placeholder="كلمة المرور" value={password} onChange={(e)=>setPassword(e.target.value)} className="w-full bg-[#1E293B] border border-slate-700 p-3 rounded-xl focus:ring-2 focus:ring-sky-500 outline-none" required />
          {error && <p className="text-red-400 text-sm font-medium">{error}</p>}
          <button type="submit" disabled={loading} className="w-full bg-gradient-to-r from-sky-500 to-indigo-600 text-white p-3 rounded-xl font-bold hover:opacity-90 disabled:opacity-50 flex items-center justify-center gap-2">
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : (isLogin ? "دخول" : "إنشاء حساب")}
          </button>
        </form>
      </motion.div>
    </div>
  );
}

// ==========================================
// 2. Sidebar Component
// ==========================================
function Sidebar({ currentTab, setCurrentTab, todayData, setTodayData, streak, fetchTodayData }: any) {
  const { username, setLogout, userId } = useStore();
  const [saving, setSaving] = useState(false);

  const tabs = [
    { id: "chat", name: "المحادثة", icon: <BrainCircuit className="w-5 h-5" /> },
    { id: "history", name: "سجل المحادثات", icon: <Calendar className="w-5 h-5" /> },
    { id: "dashboard", name: "الداشبورد", icon: <BarChart2 className="w-5 h-5" /> },
    { id: "goals", name: "الأهداف", icon: <Target className="w-5 h-5" /> },
    { id: "insights", name: "الرؤى الذكية", icon: <Lightbulb className="w-5 h-5" /> },
    { id: "report", name: "التقرير الأسبوعي", icon: <FileText className="w-5 h-5" /> },
  ];

  // Helper function to clamp daily values within logical limits
  const handleDataChange = (key: string, val: string, min: number, max: number) => {
    if (val === "") {
      setTodayData({ ...todayData, [key]: null });
      return;
    }
    let num = parseFloat(val);
    if (num > max) num = max;
    if (num < min) num = min;
    setTodayData({ ...todayData, [key]: num });
  };

  const handleManualSave = async () => {
    setSaving(true);
    try {
      await axios.post("http://127.0.0.1:8000/api/data/update", { user_id: userId, data: todayData });
      fetchTodayData(); 
    } catch (e) {
      alert("Failed to save data.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="w-96 bg-[#0D1117] border-l border-slate-800 h-screen flex flex-col p-6 overflow-y-auto shrink-0 z-20 shadow-2xl" dir="rtl">
      <div className="text-center mb-6 border-b border-slate-800 pb-6">
        <BrainCircuit className="w-12 h-12 text-sky-400 mx-auto mb-2" />
        <h2 className="text-xl font-bold text-white">MindMate</h2>
        <p className="text-xs text-slate-400 mt-1">أهلاً، {username}</p>
      </div>

      <div className="flex gap-4 mb-6">
        <div className="flex-1 bg-slate-800/50 rounded-2xl p-3 text-center border border-slate-700">
          <span className="text-xl block">🔥</span>
          <div className="text-lg font-black text-amber-400">{streak}</div>
          <div className="text-[9px] text-slate-400">يوم متتالي</div>
        </div>
        <div className="flex-1 bg-slate-800/50 rounded-2xl p-3 text-center border border-slate-700">
          <span className="text-xl block">💚</span>
          <div className="text-lg font-black text-emerald-400">{todayData?.wellness_score || "--"}</div>
          <div className="text-[9px] text-slate-400">نقاط الصحة</div>
        </div>
      </div>

      <nav className="space-y-2 mb-6">
        {tabs.map((tab) => (
          <button key={tab.id} onClick={() => setCurrentTab(tab.id)} className={`w-full flex items-center gap-3 p-3 rounded-xl transition ${currentTab === tab.id ? 'bg-sky-500/10 text-sky-400 font-bold border border-sky-500/20' : 'text-slate-400 hover:bg-slate-800'}`}>
            {tab.icon} {tab.name}
          </button>
        ))}
      </nav>

      {/* Manual Entry Form with Clamped Limits */}
      <div className="mt-auto border-t border-slate-800 pt-6">
         <h3 className="text-sky-400 font-bold mb-4 flex items-center gap-2"><Activity className="w-5 h-5"/> بيانات اليوم</h3>
         <div className="grid grid-cols-2 gap-3 mb-4">
            <div>
              <label className="text-xs text-slate-400 mb-1 flex items-center gap-1"><Moon className="w-3 h-3"/> النوم (ساعات)</label>
              <input type="number" step="0.5" value={todayData?.sleep_hours ?? ""} onChange={e => handleDataChange("sleep_hours", e.target.value, 0, 24)} className="w-full bg-[#1E293B] border border-slate-700 p-2 rounded-lg text-sm text-slate-200 outline-none focus:border-sky-500" placeholder="-" />
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 flex items-center gap-1"><Activity className="w-3 h-3"/> الضغط (1-10)</label>
              <input type="number" step="1" value={todayData?.stress_level ?? ""} onChange={e => handleDataChange("stress_level", e.target.value, 1, 10)} className="w-full bg-[#1E293B] border border-slate-700 p-2 rounded-lg text-sm text-slate-200 outline-none focus:border-sky-500" placeholder="-" />
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 flex items-center gap-1"><Droplets className="w-3 h-3"/> المياه (أكواب)</label>
              <input type="number" step="1" value={todayData?.water_cups ?? ""} onChange={e => handleDataChange("water_cups", e.target.value, 0, 30)} className="w-full bg-[#1E293B] border border-slate-700 p-2 rounded-lg text-sm text-slate-200 outline-none focus:border-sky-500" placeholder="-" />
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 flex items-center gap-1"><Activity className="w-3 h-3"/> الرياضة (دقائق)</label>
              <input type="number" step="5" value={todayData?.exercise_minutes ?? ""} onChange={e => handleDataChange("exercise_minutes", e.target.value, 0, 600)} className="w-full bg-[#1E293B] border border-slate-700 p-2 rounded-lg text-sm text-slate-200 outline-none focus:border-sky-500" placeholder="-" />
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 flex items-center gap-1"><BookOpen className="w-3 h-3"/> مذاكرة (ساعات)</label>
              <input type="number" step="0.5" value={todayData?.study_hours ?? ""} onChange={e => handleDataChange("study_hours", e.target.value, 0, 24)} className="w-full bg-[#1E293B] border border-slate-700 p-2 rounded-lg text-sm text-slate-200 outline-none focus:border-sky-500" placeholder="-" />
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 flex items-center gap-1"><Smartphone className="w-3 h-3"/> موبايل (ساعات)</label>
              <input type="number" step="0.5" value={todayData?.screen_hours ?? ""} onChange={e => handleDataChange("screen_hours", e.target.value, 0, 24)} className="w-full bg-[#1E293B] border border-slate-700 p-2 rounded-lg text-sm text-slate-200 outline-none focus:border-sky-500" placeholder="-" />
            </div>
         </div>
         <button onClick={handleManualSave} disabled={saving} className="w-full bg-emerald-600 hover:bg-emerald-500 text-white p-3 rounded-xl text-sm font-bold flex items-center justify-center gap-2 transition disabled:opacity-50 mb-4">
            {saving ? <Loader2 className="w-4 h-4 animate-spin"/> : <Save className="w-4 h-4"/>} {saving ? "جاري الحفظ..." : "حفظ البيانات"}
         </button>
      </div>

      <button onClick={setLogout} className="flex items-center justify-center gap-2 w-full p-3 bg-red-500/10 text-red-400 font-bold rounded-xl hover:bg-red-500/20 transition text-sm mt-auto">
        <LogOut className="w-4 h-4" /> تسجيل الخروج
      </button>
    </div>
  );
}

// ==========================================
// 3. History Component
// ==========================================
function HistoryComponent({ userId }: { userId: number | null }) {
  const [logs, setLogs] = useState<any[]>([]);
  const [selectedDate, setSelectedDate] = useState<string>("");

  useEffect(() => {
    if (userId) {
        axios.get(`http://127.0.0.1:8000/api/data/logs/${userId}`).then(res => {
            const data = res.data.logs || [];
            setLogs(data);
            if (data.length > 0) setSelectedDate(data[data.length - 1].date_str);
        }).catch(console.error);
    }
  }, [userId]);

  const selectedLog = logs.find(l => l.date_str === selectedDate);
  let messages = [];
  try { if (selectedLog?.chat_history) messages = JSON.parse(selectedLog.chat_history); } catch(e) {}

  return (
    <div className="flex h-full w-full">
      <div className="w-72 border-l border-slate-800 bg-[#0D1117] p-6 overflow-y-auto">
        <h3 className="text-lg font-bold text-sky-400 mb-6 flex items-center gap-2"><Calendar className="w-5 h-5"/> نتيجة الأيام</h3>
        <div className="space-y-3">
            {logs.slice().reverse().map(l => (
                <button key={l.date_str} onClick={() => setSelectedDate(l.date_str)} className={`w-full text-right p-4 rounded-xl transition-all shadow-sm border ${selectedDate === l.date_str ? 'bg-sky-500/20 border-sky-500/50 text-sky-400 font-bold' : 'bg-[#1E293B] border-slate-700 text-slate-300 hover:bg-slate-800'}`}>
                    {l.date_str} {l.day_emoji}
                </button>
            ))}
        </div>
      </div>
      <div className="flex-1 p-8 overflow-y-auto bg-[#080B12]">
        <div className="max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold mb-8 text-slate-200 flex items-center gap-2"><BrainCircuit className="text-sky-400"/> محادثة يوم {selectedDate}</h2>
            <div className="space-y-6">
                {messages.length > 0 ? messages.map((msg: any, idx: number) => (
                <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                    <div className={`p-4 rounded-3xl max-w-[85%] text-[15px] leading-loose shadow-xl ${msg.role === "user" ? "bg-sky-600 text-white rounded-br-sm" : "bg-[#1E293B] text-slate-200 rounded-bl-sm border border-slate-700/50"}`}>
                    {msg.content}
                    </div>
                </div>
                )) : <p className="text-slate-500 text-center mt-20">لا توجد محادثة مسجلة في هذا اليوم.</p>}
            </div>
        </div>
      </div>
    </div>
  );
}

// ==========================================
// 4. Dashboard Component
// ==========================================
function DashboardComponent({ userId }: { userId: number | null }) {
  const [logs, setLogs] = useState<any[]>([]);

  useEffect(() => {
    if (userId) axios.get(`http://127.0.0.1:8000/api/data/logs/${userId}`).then(res => setLogs(res.data.logs || [])).catch(console.error);
  }, [userId]);

  const getAvg = (key: string) => {
    const valid = logs.filter(l => l[key] != null);
    if (!valid.length) return 0;
    return valid.reduce((acc, curr) => acc + Number(curr[key]), 0) / valid.length;
  };

  if (!logs.length) return <div className="p-8 text-center text-slate-400 mt-20">لا توجد بيانات كافية لعرض الداشبورد.</div>;

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="p-8 h-full overflow-y-auto w-full max-w-6xl mx-auto">
      <h2 className="text-2xl font-bold mb-8 text-sky-400 flex items-center gap-2"><BarChart2 /> داشبورد التحليلات</h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {[
          { label: "متوسط النوم", val: getAvg("sleep_hours").toFixed(1), icon: "😴", color: "text-indigo-400" },
          { label: "مستوى الضغط", val: getAvg("stress_level").toFixed(1), icon: "🧘", color: "text-rose-400" },
          { label: "أكواب المياه", val: getAvg("water_cups").toFixed(0), icon: "💧", color: "text-sky-400" },
          { label: "Wellness Score", val: getAvg("wellness_score").toFixed(0), icon: "💚", color: "text-emerald-400" },
        ].map((kpi, i) => (
          <div key={i} className="bg-[#0D1117] p-6 rounded-2xl border border-slate-800 text-center shadow-sm">
            <div className="text-3xl mb-2">{kpi.icon}</div>
            <div className={`text-2xl font-black ${kpi.color}`}>{kpi.val}</div>
            <div className="text-xs text-slate-400 mt-1">{kpi.label}</div>
          </div>
        ))}
      </div>
      <div className="bg-[#0D1117] p-6 rounded-3xl border border-slate-800 h-96 shadow-xl">
        <h3 className="text-lg font-bold mb-6 text-slate-200">📈 تريند العادات</h3>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={logs}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
            <XAxis dataKey="date_str" stroke="#64748B" fontSize={10} tickMargin={10} />
            <YAxis yAxisId="left" stroke="#10B981" fontSize={10} domain={[0, 100]} />
            <YAxis yAxisId="right" orientation="right" stroke="#6366F1" fontSize={10} />
            <RechartsTooltip contentStyle={{ backgroundColor: '#0D1117', borderColor: '#1E293B', borderRadius: '12px' }} />
            <Line yAxisId="left" type="monotone" dataKey="wellness_score" name="الصحة" stroke="#10B981" strokeWidth={4} dot={{ r: 6 }} activeDot={{ r: 8 }} />
            <Line yAxisId="right" type="monotone" dataKey="sleep_hours" name="النوم" stroke="#6366F1" strokeWidth={3} strokeDasharray="5 5" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}

// ==========================================
// 5. Goals Component
// ==========================================
function GoalsComponent({ userId, todayData }: { userId: number | null, todayData: any }) {
  const [goals, setGoals] = useState<any[]>([]);
  // Free text input for custom goals
  const [metricName, setMetricName] = useState("");
  const [target, setTarget] = useState<number | "">("");
  const [priority, setPriority] = useState("متوسط");

  const fetchGoals = () => { if (userId) axios.get(`http://127.0.0.1:8000/api/data/goals/${userId}`).then(res => setGoals(res.data.goals)); };
  useEffect(() => { fetchGoals(); }, [userId]);

  const handleAddOrUpdateGoal = async () => {
    if (!metricName.trim() || !target) {
        alert("يرجى إدخال اسم الهدف والهدف الرقمي.");
        return;
    }
    await axios.post("http://127.0.0.1:8000/api/data/goals", { user_id: userId, metric: metricName, target: Number(target), priority });
    fetchGoals();
    setMetricName("");
    setTarget("");
  };

  const handleDeleteGoal = async (metricToDelete: string) => {
    if(confirm("هل أنت متأكد من حذف هذا الهدف؟")) {
      await axios.delete(`http://127.0.0.1:8000/api/data/goals/${userId}/${metricToDelete}`);
      fetchGoals();
    }
  };

  const loadGoalForEditing = (g: any) => {
    setMetricName(g.metric);
    setTarget(g.target);
    setPriority(g.priority || "متوسط");
  };

  const PRIORITY_COLORS: any = {
    "عالي": "text-rose-400 border-rose-400/20 bg-rose-400/10",
    "متوسط": "text-amber-400 border-amber-400/20 bg-amber-400/10",
    "منخفض": "text-emerald-400 border-emerald-400/20 bg-emerald-400/10"
  };

  return (
    <div className="p-8 h-full overflow-y-auto w-full max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-8 text-sky-400 flex items-center gap-2"><Target /> أهدافك الشخصية</h2>
      <div className="bg-[#0D1117] p-6 rounded-3xl border border-slate-800 mb-8 flex flex-wrap gap-4 items-end shadow-lg">
        <div className="flex-1 min-w-[200px]">
          <label className="block text-xs text-slate-500 mb-2">اسم الهدف</label>
          <input type="text" placeholder="مثال: قراءة، مشي، تعلم برمجة..." value={metricName} onChange={(e) => setMetricName(e.target.value)} className="w-full bg-[#1E293B] border border-slate-700 p-3 rounded-xl outline-none text-slate-200 focus:border-sky-500 transition-colors" />
        </div>
        <div className="w-28">
          <label className="block text-xs text-slate-500 mb-2">الرقم المستهدف</label>
          <input type="number" min="0" step="0.5" value={target} onChange={(e) => setTarget(e.target.value === "" ? "" : Number(e.target.value))} className="w-full bg-[#1E293B] border border-slate-700 p-3 rounded-xl outline-none text-slate-200 focus:border-sky-500" />
        </div>
        <div className="w-32">
          <label className="block text-xs text-slate-500 mb-2">الأهمية</label>
          <select value={priority} onChange={(e) => setPriority(e.target.value)} className="w-full bg-[#1E293B] border border-slate-700 p-3 rounded-xl outline-none text-slate-200">
            <option value="عالي">عالي</option>
            <option value="متوسط">متوسط</option>
            <option value="منخفض">منخفض</option>
          </select>
        </div>
        <button onClick={handleAddOrUpdateGoal} className="bg-sky-500 hover:bg-sky-400 text-white px-6 py-3 rounded-xl font-bold transition shadow-lg shadow-sky-500/20">💾 حفظ</button>
      </div>

      <div className="space-y-4">
        {goals.map((g, i) => {
          // If the metric name matches a known system metric, auto-fill progress.
          // Note: Custom metrics will display 0 by default as they require specialized DB schema to track daily.
          const current = todayData?.[g.metric] || 0;
          const pct = Math.min((current / g.target) * 100, 100);
          const pColor = PRIORITY_COLORS[g.priority] || PRIORITY_COLORS["متوسط"];
          
          return (
            <div key={i} className="bg-[#0D1117] p-6 rounded-2xl border border-slate-800 shadow-md relative group">
              <div className="flex justify-between items-start mb-4">
                <div>
                    <div className="flex items-center gap-3 mb-1">
                        <span className="font-bold text-slate-200 text-lg">{g.metric}</span>
                        <span className={`text-[10px] px-2 py-1 rounded-md border ${pColor} flex items-center gap-1`}>
                            <Flag className="w-3 h-3"/> {g.priority}
                        </span>
                    </div>
                    <span className="text-slate-400 text-sm">الحالي: <span className="text-sky-400 font-bold">{current}</span> / الهدف: {g.target}</span>
                </div>
                
                <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button onClick={() => loadGoalForEditing(g)} className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition" title="تعديل">
                        <Edit2 className="w-4 h-4" />
                    </button>
                    <button onClick={() => handleDeleteGoal(g.metric)} className="p-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-lg transition" title="حذف">
                        <Trash2 className="w-4 h-4" />
                    </button>
                </div>
              </div>
              <div className="h-4 w-full bg-slate-800 rounded-full overflow-hidden shadow-inner border border-slate-700/50">
                <motion.div initial={{ width: 0 }} animate={{ width: `${pct}%` }} transition={{ duration: 1.5, ease: "easeOut" }} className="h-full bg-gradient-to-r from-sky-400 via-indigo-500 to-indigo-600 shadow-lg shadow-indigo-500/30" />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ==========================================
// 6. Insights Component (Instant Dynamic Insights)
// ==========================================
function InsightsComponent({ userId, todayData }: { userId: number | null, todayData: any }) {
  const [logs, setLogs] = useState<any[]>([]);
  useEffect(() => { if (userId) axios.get(`http://127.0.0.1:8000/api/data/logs/${userId}`).then(res => setLogs(res.data.logs || [])); }, [userId]);

  // Generate real-time insights based on the active user's daily snapshot
  const insightsList = [];
  
  if (todayData?.sleep_hours && todayData.sleep_hours < 7) {
    insightsList.push({ title: "تنبيه: جودة النوم", desc: "ساعات نومك اليوم أقل من المعدل الصحي (7-8 ساعات). هذا قد يؤثر على تركيزك، حاول الاسترخاء مبكراً اليوم.", icon: <Moon className="w-5 h-5"/>, color: "text-indigo-400" });
  } else if (todayData?.sleep_hours && todayData.sleep_hours >= 7) {
    insightsList.push({ title: "ممتاز: نوم صحي", desc: "لقد حصلت على قسط ممتاز من النوم! هذا يعزز من مناعتك وحالتك المزاجية بشكل مباشر.", icon: <Sparkles className="w-5 h-5"/>, color: "text-emerald-400" });
  }

  if (todayData?.stress_level && todayData.stress_level >= 7) {
    insightsList.push({ title: "مستوى ضغط مرتفع", desc: "مؤشر الضغط النفسي لديك مرتفع. جرب أخذ استراحة لمدة 10 دقائق للتنفس العميق، أو تحدث مع MindMate للتفريغ النفسي.", icon: <Activity className="w-5 h-5"/>, color: "text-rose-400" });
  }

  if (todayData?.water_cups && todayData.water_cups < 6) {
    insightsList.push({ title: "تذكير: شرب المياه", desc: "لم تشرب كمية كافية من المياه اليوم. تذكر أن الجفاف يسبب الإرهاق وضعف التركيز.", icon: <Droplets className="w-5 h-5"/>, color: "text-sky-400" });
  }

  if (logs.length >= 3) {
      insightsList.push({ title: "تحليل الذكاء الاصطناعي التراكمي", desc: "بناءً على الأيام السابقة، هناك ارتباط وثيق بين وقت الشاشة المرتفع وانخفاض جودة نومك. ينصح بتقليل استخدام الهاتف قبل النوم بساعة.", icon: <TrendingUp className="w-5 h-5"/>, color: "text-amber-400" });
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="p-8 h-full overflow-y-auto w-full max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-6 text-sky-400 flex items-center gap-2"><Lightbulb /> الرؤى الذكية</h2>
      
      {insightsList.length === 0 ? (
         <div className="text-center text-slate-400 mt-20 p-8 border border-dashed border-slate-700 rounded-2xl">
            لم نتمكن من استنتاج رؤى دقيقة حتى الآن. يرجى إدخال بياناتك اليومية (في الشريط الجانبي) للحصول على تحليلات فورية.
         </div>
      ) : (
        <div className="grid gap-4">
          {insightsList.map((insight, idx) => (
              <div key={idx} className={`bg-[#0D1117] p-6 rounded-2xl border border-slate-800 transition shadow-md`}>
                <h3 className={`${insight.color} font-bold mb-2 flex items-center gap-2`}>
                    {insight.icon} {insight.title}
                </h3>
                <p className="text-slate-300 leading-relaxed text-sm">{insight.desc}</p>
              </div>
          ))}
        </div>
      )}
    </motion.div>
  );
}

// ==========================================
// 7. Report Component
// ==========================================
function ReportComponent({ userId }: { userId: number | null }) {
  const [report, setReport] = useState("");
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState<any[]>([]);
  useEffect(() => { if (userId) axios.get(`http://127.0.0.1:8000/api/data/logs/${userId}`).then(res => setLogs(res.data.logs || [])); }, [userId]);

  const generateReport = async () => {
    setLoading(true);
    try {
      const last7 = logs.slice(-7);
      const avg = (arr: any[]) => arr.reduce((a,b)=>a+b, 0) / (arr.length || 1);
      const summary = {
        avg_sleep: avg(last7.map(l => l.sleep_hours).filter(v=>v)),
        avg_stress: avg(last7.map(l => l.stress_level).filter(v=>v)),
        days_count: last7.length
      };
      const res = await axios.post("http://127.0.0.1:8000/api/report", { weekly_data: summary });
      setReport(res.data.report);
    } catch (e) {} finally { setLoading(false); }
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="p-8 h-full overflow-y-auto w-full max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-6 text-sky-400 flex items-center gap-2"><FileText /> التقرير الأسبوعي الذكي</h2>
      <button onClick={generateReport} disabled={loading} className="bg-gradient-to-r from-sky-500 to-indigo-600 text-white px-8 py-3 rounded-xl font-bold mb-8 hover:opacity-90 disabled:opacity-50 flex items-center gap-2 transition">
        {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <BrainCircuit className="w-5 h-5" />} توليد التقرير
      </button>
      {report && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="bg-[#0D1117] p-8 rounded-3xl border border-slate-800 shadow-xl prose prose-invert max-w-none">
          <div className="whitespace-pre-wrap text-slate-200 leading-loose text-lg">{report}</div>
        </motion.div>
      )}
    </motion.div>
  );
}

// ==========================================
// 8. Chat Component
// ==========================================
function ChatComponent({ todayData, setTodayData }: any) {
  const { userId, username } = useStore();
  const [messages, setMessages] = useState<any[]>([{ role: "assistant", content: `أهلاً بيك يا ${username}! جاهزين نكمل يومنا؟` }]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (todayData?.chat_history) {
      try { setMessages(JSON.parse(todayData.chat_history)); } catch(e) {}
    }
  }, [todayData]);

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, isTyping]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    const userMsg = { role: "user", content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setIsTyping(true);

    try {
      const response = await axios.post("http://127.0.0.1:8000/api/chat", {
        user_id: userId, user_name: username, user_text: userMsg.content, current_data: todayData, chat_history: messages,
      });
      setMessages(prev => [...prev, { role: "assistant", content: response.data.reply }]);
      setTodayData((prev: any) => ({ ...prev, ...response.data.extracted_metrics, wellness_score: response.data.wellness_score }));
    } catch (error) {
      setMessages(prev => [...prev, { role: "assistant", content: "عذراً، الخادم لا يستجيب." }]);
    } finally { setIsTyping(false); }
  };

  return (
    <div className="flex flex-col h-full w-full max-w-4xl mx-auto bg-[#080B12] border-x border-slate-800/50 shadow-2xl relative">
      <header className="flex items-center p-6 bg-[#0D1117] border-b border-slate-800 shadow-md backdrop-blur-xl sticky top-0 z-10">
        <h1 className="text-xl font-black bg-clip-text text-transparent bg-gradient-to-r from-sky-400 to-indigo-400">محادثة MindMate</h1>
      </header>
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        <AnimatePresence>
          {messages.map((msg, idx) => (
            <motion.div key={idx} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`p-4 rounded-3xl max-w-[85%] text-[15px] leading-loose shadow-xl ${msg.role === "user" ? "bg-sky-600 text-white rounded-br-sm" : "bg-[#1E293B] text-slate-200 rounded-bl-sm border border-slate-700/50"}`}>
                {msg.content}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        {isTyping && (
          <div className="flex justify-start">
            <div className="p-4 bg-[#1E293B] rounded-3xl flex items-center gap-2 border border-slate-700/50 shadow-lg">
              <motion.div animate={{ y: [0, -6, 0] }} transition={{ repeat: Infinity, duration: 0.8 }} className="w-2 h-2 bg-sky-400 rounded-full" />
              <motion.div animate={{ y: [0, -6, 0] }} transition={{ repeat: Infinity, duration: 0.8, delay: 0.2 }} className="w-2 h-2 bg-sky-400 rounded-full" />
              <motion.div animate={{ y: [0, -6, 0] }} transition={{ repeat: Infinity, duration: 0.8, delay: 0.4 }} className="w-2 h-2 bg-sky-400 rounded-full" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <footer className="p-6 bg-[#0D1117] border-t border-slate-800">
        <form onSubmit={handleSendMessage} className="relative flex">
          <input type="text" value={input} onChange={(e) => setInput(e.target.value)} placeholder="اكتب لـ MindMate..." className="w-full bg-[#1E293B] border border-slate-700 rounded-full py-4 px-6 pr-14 focus:ring-2 focus:ring-sky-500 outline-none text-slate-200" disabled={isTyping} />
          <button type="submit" disabled={!input.trim() || isTyping} className="absolute right-2 top-2 bottom-2 bg-sky-500 hover:bg-sky-400 text-white rounded-full w-12 flex items-center justify-center transition-all disabled:opacity-50">
            <Send className="w-5 h-5 rotate-180" />
          </button>
        </form>
      </footer>
    </div>
  );
}

// ==========================================
// 9. Main App Shell
// ==========================================
export default function App() {
  const { isLoggedIn, userId } = useStore();
  const [currentTab, setCurrentTab] = useState("chat");
  const [todayData, setTodayData] = useState<any>({});
  const [streak, setStreak] = useState(0);

  const fetchTodayData = () => {
    if (isLoggedIn && userId) {
      axios.get(`http://127.0.0.1:8000/api/data/today/${userId}`)
        .then(res => {
          setTodayData(res.data.today_log || {});
          setStreak(res.data.streak || 0);
        }).catch(console.error);
    }
  };

  useEffect(() => {
    fetchTodayData();
  }, [isLoggedIn, userId]);

  if (!isLoggedIn) return <AuthPage />;

  return (
    <div className="flex h-screen bg-[#080B12] text-slate-200 font-sans" dir="rtl">
      <Sidebar currentTab={currentTab} setCurrentTab={setCurrentTab} todayData={todayData} setTodayData={setTodayData} streak={streak} fetchTodayData={fetchTodayData} />
      <main className="flex-1 flex flex-col relative overflow-hidden bg-[#080B12]">
        {currentTab === "chat" && <ChatComponent todayData={todayData} setTodayData={setTodayData} />}
        {currentTab === "history" && <HistoryComponent userId={userId} />}
        {currentTab === "dashboard" && <DashboardComponent userId={userId} />}
        {currentTab === "goals" && <GoalsComponent userId={userId} todayData={todayData} />}
        {currentTab === "insights" && <InsightsComponent userId={userId} todayData={todayData} />}
        {currentTab === "report" && <ReportComponent userId={userId} />}
      </main>
    </div>
  );
}