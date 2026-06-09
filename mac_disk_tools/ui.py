# -*- coding: utf-8 -*-

HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mac Disk Space Analyzer</title>
<style>
  :root {
    --bg:#0f1117;--card:#1a1d27;--card2:#20232f;--border:#2e3140;
    --text:#e2e4ef;--sub:#8b8fa8;--accent:#5b8ef0;
    --safe:#34d399;--caution:#fbbf24;--danger:#f87171;--manual:#a78bfa;
    --radius:12px;
  }
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:var(--bg);color:var(--text);font-family:-apple-system,"PingFang SC",sans-serif;min-height:100vh}

  header{background:var(--card);border-bottom:1px solid var(--border);padding:16px 26px;display:flex;align-items:center;gap:12px;position:sticky;top:0;z-index:10}
  .logo{width:38px;height:38px;background:linear-gradient(135deg,#1e2235,#2a2f4a);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0}
  header h1{font-size:18px;font-weight:700}
  header p{font-size:12px;color:var(--sub);margin-top:1px}
  .lang-switch{margin-left:auto;display:flex;align-items:center;gap:6px}
  .lang-btn{background:var(--card2);border:1px solid var(--border);color:var(--sub);border-radius:8px;padding:7px 10px;font-size:12px;cursor:pointer}
  .lang-btn.active{border-color:var(--accent);color:var(--text);background:rgba(91,142,240,.15)}
  .scan-btn{margin-left:auto;background:var(--accent);color:#fff;border:none;border-radius:8px;padding:9px 20px;font-size:13px;font-weight:600;cursor:pointer;transition:opacity .2s;white-space:nowrap}
  .scan-btn:hover{opacity:.85}.scan-btn:disabled{opacity:.4;cursor:not-allowed}

  #disk-section{padding:20px 26px 0}
  .disk-card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:18px 22px}
  .disk-header{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:10px}
  .disk-title{font-size:14px;font-weight:600}
  .bar-wrap{background:var(--border);border-radius:6px;height:10px;overflow:hidden}
  .bar-fill{height:100%;border-radius:6px;transition:width .9s ease;background:linear-gradient(90deg,var(--accent),#a78bfa)}
  .disk-stats{display:flex;gap:24px;margin-top:12px;flex-wrap:wrap}
  .stat{font-size:13px}.stat span{color:var(--sub)}

  #filters{padding:16px 26px 0;display:flex;gap:8px;flex-wrap:wrap;align-items:center}
  .filter-btn{background:var(--card);border:1px solid var(--border);color:var(--sub);padding:5px 14px;border-radius:20px;font-size:12px;cursor:pointer;transition:all .15s}
  .filter-btn:hover,.filter-btn.active{background:var(--accent);border-color:var(--accent);color:#fff}
  .filter-sep{flex:1;min-width:12px}
  .sort-wrap{display:flex;align-items:center;gap:6px;font-size:12px;color:var(--sub)}
  .sort-wrap select{background:var(--card);color:var(--text);border:1px solid var(--border);border-radius:6px;padding:4px 8px;font-size:12px;cursor:pointer}

  #summary{padding:12px 26px 0;font-size:12px;color:var(--sub)}

  #legend{padding:10px 26px 0;display:flex;gap:14px;flex-wrap:wrap}
  .leg{display:flex;align-items:center;gap:5px;font-size:11px;color:var(--sub)}
  .leg-dot{width:7px;height:7px;border-radius:50%;flex-shrink:0}

  #filters2{padding:8px 26px 0;display:flex;gap:7px;flex-wrap:wrap;align-items:center}
  .safety-btn{background:var(--card);border:1px solid var(--border);color:var(--sub);padding:4px 12px;border-radius:20px;font-size:12px;cursor:pointer;transition:all .15s;white-space:nowrap}
  .safety-btn:hover{border-color:#555}
  .safety-btn.active{border-color:var(--accent);color:var(--text);background:rgba(91,142,240,.12)}
  .search-wrap{display:flex;align-items:center;background:var(--card);border:1px solid var(--border);border-radius:8px;overflow:hidden;min-width:200px}
  .search-wrap:focus-within{border-color:var(--accent)}
  #searchBox{background:transparent;border:none;outline:none;color:var(--text);font-size:12px;padding:5px 10px;flex:1;min-width:0}
  #searchBox::placeholder{color:var(--sub)}
  .clear-btn{background:transparent;border:none;color:var(--sub);cursor:pointer;padding:4px 8px;font-size:12px;line-height:1;transition:color .15s}
  .clear-btn:hover{color:var(--text)}

  #loading{display:none;padding:60px 26px;text-align:center;color:var(--sub);font-size:14px}
  .spinner{width:34px;height:34px;border:3px solid var(--border);border-top-color:var(--accent);border-radius:50%;animation:spin .8s linear infinite;margin:0 auto 14px}
  @keyframes spin{to{transform:rotate(360deg)}}

  #grid{padding:16px 26px 48px;display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:12px}
  .card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:15px 17px;display:flex;flex-direction:column;gap:9px;transition:border-color .2s}
  .card:hover{border-color:#444766}

  .card-top{display:flex;align-items:flex-start;justify-content:space-between;gap:10px}
  .card-info{flex:1;min-width:0}
  .card-name{font-size:14px;font-weight:600;display:flex;align-items:center;gap:6px}
  .card-cat{font-size:10px;background:rgba(91,142,240,.15);color:var(--accent);padding:1px 7px;border-radius:10px;font-weight:500;flex-shrink:0}
  .card-path{font-size:10px;color:var(--sub);margin-top:3px;word-break:break-all;font-family:"SF Mono",monospace;opacity:.8}
  .card-size{font-size:19px;font-weight:700;flex-shrink:0}
  .card-size.na{font-size:12px;color:var(--sub);font-weight:400;margin-top:4px}

  .card-desc{font-size:12px;color:var(--sub);line-height:1.55}

  .card-footer{display:flex;align-items:center;justify-content:space-between;gap:8px}
  .badge{font-size:10px;font-weight:600;padding:2px 8px;border-radius:20px;white-space:nowrap}
  .badge-safe{background:rgba(52,211,153,.15);color:var(--safe)}
  .badge-caution{background:rgba(251,191,36,.15);color:var(--caution)}
  .badge-danger{background:rgba(248,113,113,.15);color:var(--danger)}
  .badge-manual{background:rgba(167,139,250,.15);color:var(--manual)}

  .mini-bar-wrap{flex:1;background:var(--border);border-radius:3px;height:3px;overflow:hidden}
  .mini-bar-fill{height:100%;border-radius:3px;background:var(--accent);transition:width .9s ease}

  .open-btn,.drill-card-btn{background:rgba(91,142,240,.1);border:1px solid rgba(91,142,240,.2);border-radius:7px;padding:4px 8px;font-size:13px;cursor:pointer;transition:all .15s;line-height:1}
  .open-btn:hover,.drill-card-btn:hover{background:rgba(91,142,240,.25)}
  .del-btn{background:rgba(248,113,113,.1);color:var(--danger);border:1px solid rgba(248,113,113,.2);border-radius:7px;padding:4px 12px;font-size:11px;font-weight:600;cursor:pointer;transition:all .15s;white-space:nowrap}
  .del-btn:hover{background:rgba(248,113,113,.22)}
  .del-btn:disabled{opacity:.45;cursor:not-allowed;color:var(--sub);border-color:var(--border);background:rgba(255,255,255,.04)}
  .del-btn.gone{background:rgba(52,211,153,.1);color:var(--safe);border-color:rgba(52,211,153,.2);cursor:default}

  #empty{display:none;padding:50px 26px;text-align:center;color:var(--sub);font-size:13px}

  /* ── 下钻面板 ── */
  #drill-overlay{position:fixed;inset:0;background:rgba(0,0,0,.55);backdrop-filter:blur(4px);z-index:900;display:flex;justify-content:flex-end}
  #drill-panel{background:var(--card2);border-left:1px solid var(--border);width:min(560px,95vw);height:100%;display:flex;flex-direction:column;animation:slideIn .25s ease}
  @keyframes slideIn{from{transform:translateX(100%)}to{transform:translateX(0)}}
  #drill-header{padding:16px 18px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:10px;flex-shrink:0}
  #drill-breadcrumb{flex:1;font-size:12px;color:var(--sub);word-break:break-all;line-height:1.5}
  #drill-breadcrumb span{cursor:pointer;color:var(--accent)}
  #drill-breadcrumb span:hover{text-decoration:underline}
  .drill-close{background:transparent;border:none;color:var(--sub);font-size:16px;cursor:pointer;padding:4px 8px;border-radius:6px;line-height:1}
  .drill-close:hover{background:var(--border)}
  #drill-body{flex:1;overflow-y:auto;padding:10px 0}
  .drill-row{display:flex;align-items:center;gap:10px;padding:9px 18px;cursor:pointer;transition:background .12s;border-bottom:1px solid rgba(255,255,255,.03)}
  .drill-row:hover{background:rgba(255,255,255,.04)}
  .drill-icon{font-size:15px;flex-shrink:0;width:20px;text-align:center}
  .drill-name{flex:1;font-size:13px;word-break:break-all;min-width:0}
  .drill-name.hidden{color:var(--sub);opacity:.6}
  .drill-size{font-size:12px;color:var(--sub);flex-shrink:0;min-width:64px;text-align:right}
  .drill-bar-wrap{width:80px;background:var(--border);border-radius:3px;height:3px;flex-shrink:0}
  .drill-bar-fill{height:100%;border-radius:3px;background:var(--accent)}
  .drill-actions{display:flex;gap:6px;flex-shrink:0}
  .drill-open-btn{background:rgba(91,142,240,.1);color:var(--accent);border:1px solid rgba(91,142,240,.2);border-radius:6px;padding:3px 9px;font-size:11px;cursor:pointer}
  .drill-open-btn:hover{background:rgba(91,142,240,.22)}
  .drill-del-btn{background:rgba(248,113,113,.08);color:var(--danger);border:1px solid rgba(248,113,113,.18);border-radius:6px;padding:3px 9px;font-size:11px;cursor:pointer}
  .drill-del-btn:hover{background:rgba(248,113,113,.2)}
  .drill-del-btn:disabled{opacity:.35;cursor:not-allowed;color:var(--sub);border-color:var(--border);background:rgba(255,255,255,.04)}
  .drill-loading{padding:30px;text-align:center;color:var(--sub);font-size:13px}
  .drill-err{padding:20px 18px;color:var(--danger);font-size:13px}
  .drill-empty{padding:30px;text-align:center;color:var(--sub);font-size:13px}

  .overlay{position:fixed;inset:0;background:rgba(0,0,0,.65);backdrop-filter:blur(5px);display:flex;align-items:center;justify-content:center;z-index:999}
  .modal{background:var(--card2);border:1px solid var(--border);border-radius:16px;padding:26px;max-width:400px;width:90%}
  .modal h2{font-size:16px;margin-bottom:8px}
  .modal p{font-size:13px;color:var(--sub);line-height:1.55;margin-bottom:8px}
  .modal code{background:var(--bg);padding:3px 8px;border-radius:5px;font-family:"SF Mono",monospace;font-size:11px;color:var(--text);word-break:break-all;display:block;margin:8px 0 14px}
  .modal-btns{display:flex;gap:10px;justify-content:flex-end;margin-top:6px}
  .btn-cancel{background:var(--border);color:var(--text);border:none;border-radius:8px;padding:8px 16px;font-size:13px;cursor:pointer}
  .btn-confirm{background:var(--danger);color:#fff;border:none;border-radius:8px;padding:8px 16px;font-size:13px;font-weight:600;cursor:pointer}
  .btn-confirm:hover{opacity:.85}

  #toast{position:fixed;bottom:26px;left:50%;transform:translateX(-50%) translateY(16px);background:var(--card2);border:1px solid var(--border);color:var(--text);padding:9px 20px;border-radius:10px;font-size:13px;opacity:0;transition:all .3s;pointer-events:none;white-space:nowrap;z-index:1000}
  #toast.show{opacity:1;transform:translateX(-50%) translateY(0)}

  .welcome{padding:60px 26px;text-align:center}
  .welcome .icon{font-size:56px;margin-bottom:16px}
  .welcome h2{font-size:20px;font-weight:700;margin-bottom:8px}
  .welcome p{font-size:13px;color:var(--sub);max-width:380px;margin:0 auto;line-height:1.65}
  .welcome ul{list-style:none;display:flex;flex-direction:column;gap:6px;margin-top:18px;max-width:340px;margin-left:auto;margin-right:auto}
  .welcome ul li{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:8px 14px;font-size:12px;color:var(--sub);text-align:left;display:flex;align-items:center;gap:8px}
</style>
</head>
<body>

<header>
  <div class="logo">🔍</div>
  <div>
    <h1 id="appTitle"></h1>
    <p id="appSubtitle"></p>
  </div>
  <div class="lang-switch">
    <button class="lang-btn active" data-lang="zh" onclick="setLanguage('zh', this)">中文</button>
    <button class="lang-btn" data-lang="en" onclick="setLanguage('en', this)">EN</button>
  </div>
  <button class="scan-btn" id="scanBtn" onclick="startScan()">🔍 开始扫描</button>
</header>

<div id="welcome" class="welcome">
  <div class="icon">💾</div>
  <h2 id="welcomeTitle"></h2>
  <p id="welcomeDesc"></p>
  <ul id="welcomeList">
  </ul>
</div>

<section id="disk-section" style="display:none">
  <div class="disk-card">
    <div class="disk-header">
      <span class="disk-title" id="diskTitle"></span>
      <span style="font-size:13px;color:var(--sub)" id="disk-pct"></span>
    </div>
    <div class="bar-wrap"><div class="bar-fill" id="disk-bar" style="width:0%"></div></div>
    <div class="disk-stats">
      <div class="stat"><span id="labelUsed"></span><strong id="d-used"></strong></div>
      <div class="stat"><span id="labelAvail"></span><strong id="d-avail"></strong></div>
      <div class="stat"><span id="labelTotal"></span><strong id="d-total"></strong></div>
    </div>
  </div>
</section>

<section id="filters" style="display:none">
  <button class="filter-btn active" data-filter-key="all" onclick="setFilter('all',this)"></button>
  <button class="filter-btn" data-filter-key="caches_logs" onclick="setFilter('缓存 & 日志',this)"></button>
  <button class="filter-btn" data-filter-key="personal_files" onclick="setFilter('个人文件',this)"></button>
  <button class="filter-btn" data-filter-key="app_data" onclick="setFilter('应用数据',this)"></button>
  <button class="filter-btn" data-filter-key="virtual_machines" onclick="setFilter('虚拟机',this)"></button>
  <div class="sort-wrap" style="margin-left:4px"><span id="categoryLabel"></span>
    <select id="categorySelect" onchange="setFilterSelect(this.value)">
      <option value="" data-select-key="more_categories"></option>
      <optgroup data-group-key="dev_languages">
        <option value="Apple 开发" data-option-key="apple_dev"></option>
        <option value="Node.js / 前端" data-option-key="node_frontend"></option>
        <option value="Python" data-option-key="python"></option>
        <option value="Java / JVM" data-option-key="java_jvm"></option>
        <option value="Go" data-option-key="go"></option>
        <option value="Rust" data-option-key="rust"></option>
        <option value="Flutter / Dart" data-option-key="flutter_dart"></option>
        <option value="Ruby" data-option-key="ruby"></option>
        <option value="PHP" data-option-key="php"></option>
        <option value="Android 开发" data-option-key="android_dev"></option>
        <option value="其他语言" data-option-key="other_languages"></option>
        <option value="其他开发工具" data-option-key="other_dev_tools"></option>
      </optgroup>
      <optgroup data-group-key="tools_services">
        <option value="IDE & 编辑器" data-option-key="ides_editors"></option>
        <option value="AI / 机器学习" data-option-key="ai_ml"></option>
        <option value="数据库" data-option-key="databases"></option>
        <option value="云服务 CLI" data-option-key="cloud_service_clis"></option>
        <option value="安全 & 调试" data-option-key="security_debugging"></option>
      </optgroup>
      <optgroup data-group-key="apps_media">
        <option value="浏览器" data-option-key="browsers"></option>
        <option value="即时通讯" data-option-key="messaging"></option>
        <option value="云存储" data-option-key="cloud_storage"></option>
        <option value="媒体制作" data-option-key="media_production"></option>
        <option value="设计工具" data-option-key="design_tools"></option>
        <option value="游戏 & 娱乐" data-option-key="gaming_entertainment"></option>
        <option value="笔记 & 知识" data-option-key="notes_knowledge"></option>
      </optgroup>
      <optgroup data-group-key="system_group">
        <option value="系统" data-option-key="system"></option>
      </optgroup>
    </select>
  </div>
  <div class="filter-sep"></div>
  <div class="sort-wrap"><span id="sortLabel"></span>
    <select id="sortSelect" onchange="doSort(this.value)">
      <option value="size" data-sort-key="size"></option>
      <option value="name" data-sort-key="name"></option>
      <option value="safety" data-sort-key="safety"></option>
    </select>
  </div>
</section>

<section id="filters2" style="display:none">
  <span style="font-size:12px;color:var(--sub);flex-shrink:0" id="safetyLabel"></span>
  <button class="safety-btn active" data-safety="" data-safety-key="all" onclick="setSafety('',this)"></button>
  <button class="safety-btn" data-safety="safe" data-safety-key="safe" onclick="setSafety('safe',this)"></button>
  <button class="safety-btn" data-safety="caution" data-safety-key="caution" onclick="setSafety('caution',this)"></button>
  <button class="safety-btn" data-safety="danger" data-safety-key="danger" onclick="setSafety('danger',this)"></button>
  <button class="safety-btn" data-safety="manual" data-safety-key="manual" onclick="setSafety('manual',this)"></button>
  <div class="filter-sep"></div>
  <div class="search-wrap">
    <input id="searchBox" type="text" oninput="doSearch(this.value)">
    <button class="clear-btn" id="clearSearchBtn" onclick="clearSearch()">✕</button>
  </div>
</section>

<div id="summary" style="display:none"></div>

<section id="legend" style="display:none">
  <div class="leg"><div class="leg-dot" style="background:var(--safe)"></div><span data-legend-key="safe"></span></div>
  <div class="leg"><div class="leg-dot" style="background:var(--caution)"></div><span data-legend-key="caution"></span></div>
  <div class="leg"><div class="leg-dot" style="background:var(--danger)"></div><span data-legend-key="danger"></span></div>
  <div class="leg"><div class="leg-dot" style="background:var(--manual)"></div><span data-legend-key="manual"></span></div>
</section>

<div id="loading"><div class="spinner"></div><span id="loadingText"></span><br><small style="display:block;margin-top:8px" id="loadingHint"></small></div>
<div id="grid"></div>
<div id="empty"></div>

<!-- 下钻面板 -->
<div id="drill-overlay" style="display:none" onclick="if(event.target===this)closeDrill()">
  <div id="drill-panel">
    <div id="drill-header">
      <div id="drill-breadcrumb"></div>
      <button class="drill-close" onclick="closeDrill()">✕</button>
    </div>
    <div id="drill-body"></div>
  </div>
</div>

<div id="modal" style="display:none">
  <div class="overlay" onclick="closeModal()">
    <div class="modal" onclick="event.stopPropagation()">
      <h2 id="modalTitle"></h2>
      <p id="modalDesc"></p>
      <code id="modal-path"></code>
      <p id="modal-warn" style="color:var(--danger);font-size:12px;display:none"></p>
      <div class="modal-btns">
        <button class="btn-cancel" id="cancelBtn" onclick="closeModal()"></button>
        <button class="btn-confirm" id="confirmBtn" onclick="confirmDelete()"></button>
      </div>
    </div>
  </div>
</div>

<div id="toast"></div>

<script>
let allItems=[], maxSize=1, currentFilter='all', currentSort='size', currentSafety='', searchQuery='', pendingDelete=null, currentLang='zh';
const I18N={
  zh:{
    htmlLang:'zh-CN', title:'Mac 磁盘分析工具', subtitle:'扫描常见路径占用 · 显示路径说明 · 一键移入废纸篓',
    scan:'🔍 开始扫描', rescan:'🔄 重新扫描', scanning:'扫描中…',
    welcomeTitle:'分析 Mac 磁盘占用', welcomeDesc:'点击「开始扫描」，工具将自动扫描系统缓存、开发工具、个人文件等常见路径，并显示每个路径的说明和安全等级。',
    welcomeList:['🟢 <strong>可安全删除</strong> — 缓存类文件，删除不影响使用','🟡 <strong>谨慎删除</strong> — 删除前请确认不再需要','🔴 <strong>不建议直接删除</strong> — 有更安全的卸载方式','🟣 <strong>手动检查</strong> — 个人文件，请自行决定'],
    diskTitle:'磁盘总览', used:'已用 ', avail:'可用 ', total:'总共 ', usedPct:'已使用',
    category:'分类：', sort:'排序：', safetyFilter:'安全等级：', searchPlaceholder:'搜索名称 / 路径 / 说明…', clearSearch:'清除搜索',
    filters:{all:'全部',caches_logs:'缓存 & 日志',personal_files:'个人文件',app_data:'应用数据',virtual_machines:'虚拟机'},
    select:{more_categories:'— 更多分类 —',dev_languages:'── 开发语言 ──',tools_services:'── 工具 & 服务 ──',apps_media:'── 应用 & 媒体 ──',system_group:'── 系统 ──'},
    options:{apple_dev:'Apple 开发（Xcode / iOS）',node_frontend:'Node.js / 前端',python:'Python',java_jvm:'Java / JVM',go:'Go',rust:'Rust',flutter_dart:'Flutter / Dart',ruby:'Ruby',php:'PHP',android_dev:'Android 开发',other_languages:'其他语言（Elixir / Haskell / .NET…）',other_dev_tools:'其他开发工具',ides_editors:'IDE & 编辑器',ai_ml:'AI / 机器学习',databases:'数据库',cloud_service_clis:'云服务 CLI',security_debugging:'安全 & 调试',browsers:'浏览器',messaging:'即时通讯',cloud_storage:'云存储',media_production:'媒体制作',design_tools:'设计工具',gaming_entertainment:'游戏 & 娱乐',notes_knowledge:'笔记 & 知识',system:'系统'},
    sorts:{size:'按大小',name:'按名称',safety:'按安全等级'},
    safety:{all:'全部',safe:'🟢 可安全删除',caution:'🟡 谨慎删除',danger:'🔴 不建议直接删除',manual:'🟣 手动检查'},
    loading:'正在扫描磁盘，请稍候…', loadingHint:'统计大目录可能需要数十秒', empty:'当前分类下没有检测到已存在的路径',
    summary:(count,size)=>`找到 ${count} 个路径，合计占用 ${size}`,
    card:{openTitle:'在 Finder 中打开', drillTitle:'查看子目录', delete:'移入废纸篓', protected:'受保护', moved:'✅ 已移入废纸篓', processing:'处理中…'},
    modal:{title:'⚠️ 确认移入废纸篓', desc:'以下路径将被移入废纸篓（可在废纸篓中恢复），之后可手动清倒废纸篓释放空间。', cancel:'取消', confirm:'确认移入废纸篓', dangerWarn:'⚠️ 此路径标记为「不建议直接删除」，请确保您了解删除后果！'},
    drill:{loading:'扫描中…', empty:'此目录为空', requestFailed:'❌ 请求失败：', openTitle:'在 Finder 中打开'},
    toast:{scanFailed:'扫描失败：', networkError:'❌ 网络错误', finderOpenFailed:'❌ 无法打开 Finder'},
    api:{missingPath:'缺少 path 参数'}
  },
  en:{
    htmlLang:'en', title:'Mac Disk Space Analyzer', subtitle:'Scan common storage paths · Explain what they contain · Move removable items to Trash',
    scan:'🔍 Start Scan', rescan:'🔄 Rescan', scanning:'Scanning…',
    welcomeTitle:'Analyze Mac Disk Usage', welcomeDesc:'Click "Start Scan" to inspect common storage-heavy locations such as system caches, developer tools, and personal files. Each item includes an explanation and a safety level.',
    welcomeList:['🟢 <strong>Safe to delete</strong> — Cache-like files that apps can recreate','🟡 <strong>Delete with caution</strong> — Confirm you no longer need them first','🔴 <strong>Not recommended</strong> — There is usually a safer uninstall or cleanup path','🟣 <strong>Manual review</strong> — Personal files, your decision'],
    diskTitle:'Disk Overview', used:'Used ', avail:'Available ', total:'Total ', usedPct:'used',
    category:'Category:', sort:'Sort:', safetyFilter:'Safety:', searchPlaceholder:'Search name / path / description…', clearSearch:'Clear search',
    filters:{all:'All',caches_logs:'Caches & Logs',personal_files:'Personal Files',app_data:'App Data',virtual_machines:'Virtual Machines'},
    select:{more_categories:'— More categories —',dev_languages:'── Dev Languages ──',tools_services:'── Tools & Services ──',apps_media:'── Apps & Media ──',system_group:'── System ──'},
    options:{apple_dev:'Apple Development (Xcode / iOS)',node_frontend:'Node.js / Frontend',python:'Python',java_jvm:'Java / JVM',go:'Go',rust:'Rust',flutter_dart:'Flutter / Dart',ruby:'Ruby',php:'PHP',android_dev:'Android Development',other_languages:'Other Languages (Elixir / Haskell / .NET…)',other_dev_tools:'Other Dev Tools',ides_editors:'IDEs & Editors',ai_ml:'AI / ML',databases:'Databases',cloud_service_clis:'Cloud Service CLIs',security_debugging:'Security & Debugging',browsers:'Browsers',messaging:'Messaging',cloud_storage:'Cloud Storage',media_production:'Media Production',design_tools:'Design Tools',gaming_entertainment:'Gaming & Entertainment',notes_knowledge:'Notes & Knowledge',system:'System'},
    sorts:{size:'By size',name:'By name',safety:'By safety'},
    safety:{all:'All',safe:'🟢 Safe to delete',caution:'🟡 Delete with caution',danger:'🔴 Not recommended',manual:'🟣 Manual review'},
    loading:'Scanning disk usage. Please wait…', loadingHint:'Large directories may take tens of seconds to measure', empty:'No existing paths were found for the current filters',
    summary:(count,size)=>`Found ${count} paths using ${size} total`,
    card:{openTitle:'Open in Finder', drillTitle:'Browse subdirectories', delete:'Move to Trash', protected:'Protected', moved:'✅ Moved to Trash', processing:'Working…'},
    modal:{title:'⚠️ Confirm Move to Trash', desc:'The following path will be moved to Trash and can be restored from Trash later. Empty Trash manually to reclaim disk space.', cancel:'Cancel', confirm:'Move to Trash', dangerWarn:'⚠️ This path is marked as "Not recommended". Make sure you understand the impact before deleting it.'},
    drill:{loading:'Scanning…', empty:'This directory is empty', requestFailed:'❌ Request failed: ', openTitle:'Open in Finder'},
    toast:{scanFailed:'Scan failed: ', networkError:'❌ Network error', finderOpenFailed:'❌ Unable to open Finder'},
    api:{missingPath:'Missing path parameter'}
  }
};
const SAFETY_LABEL={
  zh:{safe:'可安全删除',caution:'谨慎删除',danger:'不建议直接删除',manual:'手动检查'},
  en:{safe:'Safe to delete',caution:'Delete with caution',danger:'Not recommended',manual:'Manual review'}
};
const SAFETY_ORDER={safe:0,caution:1,manual:2,danger:3};

function t(){ return I18N[currentLang]; }

function setLanguage(lang, btn){
  currentLang=lang;
  localStorage.setItem('mac-disk-analyzer-lang', lang);
  document.documentElement.lang=t().htmlLang;
  document.querySelectorAll('.lang-btn').forEach(b=>b.classList.toggle('active', b.dataset.lang===lang));
  applyStaticText();
  renderCards();
}

function applyStaticText(){
  const i=t();
  document.title=i.title;
  document.getElementById('appTitle').textContent=i.title;
  document.getElementById('appSubtitle').textContent=i.subtitle;
  document.getElementById('scanBtn').textContent=allItems.length ? i.rescan : i.scan;
  document.getElementById('welcomeTitle').textContent=i.welcomeTitle;
  document.getElementById('welcomeDesc').textContent=i.welcomeDesc;
  document.getElementById('welcomeList').innerHTML=i.welcomeList.map(x=>`<li>${x}</li>`).join('');
  document.getElementById('diskTitle').textContent=i.diskTitle;
  document.getElementById('labelUsed').textContent=i.used;
  document.getElementById('labelAvail').textContent=i.avail;
  document.getElementById('labelTotal').textContent=i.total;
  document.getElementById('categoryLabel').textContent=i.category;
  document.getElementById('sortLabel').textContent=i.sort;
  document.getElementById('safetyLabel').textContent=i.safetyFilter;
  document.getElementById('searchBox').placeholder=i.searchPlaceholder;
  document.getElementById('clearSearchBtn').title=i.clearSearch;
  document.getElementById('loadingText').textContent=i.loading;
  document.getElementById('loadingHint').textContent=i.loadingHint;
  document.getElementById('empty').textContent=i.empty;
  document.getElementById('modalTitle').textContent=i.modal.title;
  document.getElementById('modalDesc').textContent=i.modal.desc;
  document.getElementById('cancelBtn').textContent=i.modal.cancel;
  document.getElementById('confirmBtn').textContent=i.modal.confirm;
  document.querySelectorAll('[data-filter-key]').forEach(el=>el.textContent=i.filters[el.dataset.filterKey]);
  document.querySelectorAll('[data-group-key]').forEach(el=>el.label=i.select[el.dataset.groupKey]);
  document.querySelectorAll('[data-select-key]').forEach(el=>el.textContent=i.select[el.dataset.selectKey]);
  document.querySelectorAll('[data-option-key]').forEach(el=>el.textContent=i.options[el.dataset.optionKey]);
  document.querySelectorAll('[data-sort-key]').forEach(el=>el.textContent=i.sorts[el.dataset.sortKey]);
  document.querySelectorAll('[data-safety-key]').forEach(el=>el.textContent=i.safety[el.dataset.safetyKey]);
  document.querySelectorAll('[data-legend-key]').forEach(el=>el.textContent=i.safety[el.dataset.legendKey]);
  renderDiskLabels();
}

function renderDiskLabels(){
  const pct=document.getElementById('disk-pct');
  if(!pct.dataset.value) return;
  pct.textContent=`${pct.dataset.value}% ${t().usedPct}`;
}

async function startScan(){
  const btn=document.getElementById('scanBtn');
  btn.disabled=true; btn.textContent=t().scanning;
  document.getElementById('welcome').style.display='none';
  document.getElementById('loading').style.display='block';
  document.getElementById('grid').innerHTML='';
  document.getElementById('disk-section').style.display='none';
  document.getElementById('filters').style.display='none';
  document.getElementById('filters2').style.display='none';
  document.getElementById('legend').style.display='none';
  document.getElementById('summary').style.display='none';
  document.getElementById('empty').style.display='none';
  // reset filters
  currentFilter='all'; currentSafety=''; searchQuery='';
  document.getElementById('searchBox').value='';
  document.querySelectorAll('.filter-btn').forEach((b,i)=>b.classList.toggle('active',i===0));
  document.querySelectorAll('.safety-btn').forEach((b,i)=>b.classList.toggle('active',i===0));
  document.getElementById('categorySelect').value='';
  try{
    const r=await fetch('/api/scan');
    const d=await r.json();
    renderDisk(d.disk_formatted);
    allItems=d.items;
    maxSize=Math.max(...allItems.filter(i=>i.size!=null).map(i=>i.size),1);
    renderCards();
    document.getElementById('disk-section').style.display='block';
    document.getElementById('filters').style.display='flex';
    document.getElementById('filters2').style.display='flex';
    document.getElementById('legend').style.display='flex';
    document.getElementById('summary').style.display='block';
  }catch(e){showToast(t().toast.scanFailed+e.message);}
  finally{
    document.getElementById('loading').style.display='none';
    btn.disabled=false; btn.textContent=t().rescan;
  }
}

function renderDisk(d){
  document.getElementById('disk-pct').dataset.value=d.percent;
  renderDiskLabels();
  const bar=document.getElementById('disk-bar');
  bar.style.width=d.percent+'%';
  bar.style.background=d.percent>85?'linear-gradient(90deg,#f87171,#fbbf24)':d.percent>70?'linear-gradient(90deg,#fbbf24,#5b8ef0)':'linear-gradient(90deg,#5b8ef0,#a78bfa)';
  document.getElementById('d-used').textContent=d.used;
  document.getElementById('d-avail').textContent=d.available;
  document.getElementById('d-total').textContent=d.total;
}

function renderCards(){
  const grid=document.getElementById('grid');
  grid.innerHTML='';
  let items=currentFilter==='all'?allItems:allItems.filter(i=>i.category===currentFilter);
  if(currentSafety) items=items.filter(i=>i.safety===currentSafety);
  if(searchQuery){
    const q=searchQuery.toLowerCase();
    items=items.filter(i=>
      i.name.toLowerCase().includes(q)||
      i.name_en.toLowerCase().includes(q)||
      i.path.toLowerCase().includes(q)||
      i.real_path.toLowerCase().includes(q)||
      i.desc.toLowerCase().includes(q)||
      i.desc_en.toLowerCase().includes(q)||
      i.category.toLowerCase().includes(q)||
      i.category_en.toLowerCase().includes(q)
    );
  }
  items=items.filter(i=>i.exists);
  if(currentSort==='size') items=[...items].sort((a,b)=>(b.size||0)-(a.size||0));
  else if(currentSort==='name') items=[...items].sort((a,b)=>getDisplayName(a).localeCompare(getDisplayName(b),currentLang==='zh'?'zh':'en'));
  else if(currentSort==='safety') items=[...items].sort((a,b)=>(SAFETY_ORDER[a.safety]??2)-(SAFETY_ORDER[b.safety]??2));

  const totalSz=items.reduce((s,i)=>s+(i.size||0),0);
  const sumEl=document.getElementById('summary');
  sumEl.textContent=t().summary(items.length, fmtBytes(totalSz));

  if(!items.length){document.getElementById('empty').style.display='block';return;}
  document.getElementById('empty').style.display='none';

  items.forEach(item=>{
    const pct=item.size?Math.round(item.size/maxSize*100):0;
    const sc={safe:'var(--safe)',caution:'var(--caution)',danger:'var(--danger)',manual:'var(--manual)'}[item.safety]||'var(--sub)';
    const safeLabel=SAFETY_LABEL[currentLang][item.safety]||'';
    const canDelete=item.deletable!==false;
    const deleteReason=getDeleteReason(item);
    const deleteLabel=canDelete?t().card.delete:t().card.protected;
    const deleteTitle=canDelete?t().card.delete:deleteReason;
    const cid='c_'+btoa(encodeURIComponent(item.path)).replace(/[^a-zA-Z0-9]/g,'');
    const div=document.createElement('div');
    div.className='card'; div.id=cid;
    div.innerHTML=`
      <div class="card-top">
        <div class="card-info">
          <div class="card-name">
            <span style="width:7px;height:7px;border-radius:50%;background:${sc};flex-shrink:0;display:inline-block"></span>
            ${esc(getDisplayName(item))}
            <span class="card-cat">${esc(getDisplayCategory(item))}</span>
          </div>
          <div class="card-path">${esc(item.real_path)}</div>
        </div>
        <div class="card-size">${esc(item.size_formatted)}</div>
      </div>
      <div class="card-desc">${esc(getDisplayDesc(item))}</div>
      <div class="card-footer">
        <span class="badge badge-${item.safety}">${safeLabel}</span>
        <div class="mini-bar-wrap"><div class="mini-bar-fill" style="width:${pct}%"></div></div>
        <div style="display:flex;gap:5px;flex-shrink:0">
          <button class="open-btn" title="${esc(t().card.openTitle)}" onclick="openInFinder('${esc(item.real_path)}',event)">📂</button>
          <button class="drill-card-btn" title="${esc(t().card.drillTitle)}" onclick="openDrill('${esc(item.real_path)}',event)">🔍</button>
          <button class="del-btn" data-path="${esc(item.path)}" data-safety="${item.safety}" data-deletable="${canDelete?'1':'0'}" data-reason-zh="${esc(item.delete_reason||'')}" data-reason-en="${esc(item.delete_reason_en||'')}" title="${esc(deleteTitle)}" onclick="askDelete(this)" ${canDelete?'':'disabled'}>${esc(deleteLabel)}</button>
        </div>
      </div>`;
    grid.appendChild(div);
  });
}

function getDisplayName(item){ return currentLang==='zh' ? item.name : item.name_en; }
function getDisplayDesc(item){ return currentLang==='zh' ? item.desc : item.desc_en; }
function getDisplayCategory(item){ return currentLang==='zh' ? item.category : item.category_en; }
function getDeleteReason(item){ return currentLang==='zh' ? (item.delete_reason||'') : (item.delete_reason_en||''); }
function getButtonDeleteReason(btn){ return currentLang==='zh' ? (btn.dataset.reasonZh||'') : (btn.dataset.reasonEn||''); }

function setFilter(cat,btn){
  currentFilter=cat;
  document.querySelectorAll('.filter-btn').forEach(b=>b.classList.remove('active'));
  if(btn) btn.classList.add('active');
  const sel=document.querySelector('#filters select');
  if(sel) sel.value='';
  renderCards();
}
function setFilterSelect(val){
  if(!val) return;
  currentFilter=val;
  document.querySelectorAll('.filter-btn').forEach(b=>b.classList.remove('active'));
  renderCards();
}
function setSafety(val,btn){
  currentSafety=val;
  document.querySelectorAll('.safety-btn').forEach(b=>b.classList.remove('active'));
  if(btn) btn.classList.add('active');
  renderCards();
}
function doSearch(val){
  searchQuery=val.trim();
  renderCards();
}
function clearSearch(){
  searchQuery='';
  document.getElementById('searchBox').value='';
  renderCards();
}
function doSort(v){currentSort=v;renderCards();}

function askDelete(btn){
  if(btn.dataset.deletable==='0'){
    const reason=getButtonDeleteReason(btn);
    if(reason) showToast(reason);
    return;
  }
  const path=btn.dataset.path, safety=btn.dataset.safety;
  pendingDelete={path,btn};
  document.getElementById('modal-path').textContent=path;
  const w=document.getElementById('modal-warn');
  if(safety==='danger'){w.textContent=t().modal.dangerWarn;w.style.display='block';}
  else{w.style.display='none';}
  document.getElementById('modal').style.display='flex';
}
function closeModal(){document.getElementById('modal').style.display='none';pendingDelete=null;}

async function confirmDelete(){
  if(!pendingDelete)return;
  const{path,btn,fromDrill}=pendingDelete;
  closeModal();
  if(btn){btn.disabled=true; btn.textContent=t().card.processing;}
  try{
    const r=await fetch('/api/delete',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path})});
    const d=await r.json();
    if(d.success){
      showToast(d.message);
      if(fromDrill){
        // 刷新下钻面板当前层
        if(drillStack.length) loadDrill(drillStack[drillStack.length-1].path);
      } else if(btn){
        btn.textContent=t().card.moved;btn.classList.add('gone');
        const card=btn.closest('.card');
        if(card){
          const sz=card.querySelector('.card-size');if(sz){sz.textContent='—';sz.classList.add('na');}
          const mb=card.querySelector('.mini-bar-fill');if(mb)mb.style.width='0%';
        }
      }
    }else{
      if(btn){btn.disabled=false;btn.textContent=t().card.delete;}
      showToast('❌ '+d.message);
    }
  }catch(e){
    if(btn){btn.disabled=false;btn.textContent=t().card.delete;}
    showToast(t().toast.networkError);
  }
}

// ── 在 Finder 中打开 ──
async function openInFinder(realPath, e){
  if(e) e.stopPropagation();
  try{
    const r=await fetch('/api/open',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:realPath})});
    const d=await r.json();
    if(!d.success) showToast('❌ '+d.message);
  }catch{showToast(t().toast.finderOpenFailed);}
}

// ── 下钻面板 ──
let drillStack=[];  // [{path, label}]

function openDrill(realPath, e){
  if(e) e.stopPropagation();
  drillStack=[{path:realPath, label:realPath}];
  document.getElementById('drill-overlay').style.display='flex';
  loadDrill(realPath);
}

function closeDrill(){
  document.getElementById('drill-overlay').style.display='none';
  drillStack=[];
}

function drillInto(path, label){
  drillStack.push({path, label});
  loadDrill(path);
}

function drillUp(idx){
  drillStack=drillStack.slice(0,idx+1);
  loadDrill(drillStack[idx].path);
}

function renderBreadcrumb(){
  const bc=document.getElementById('drill-breadcrumb');
  bc.innerHTML=drillStack.map((s,i)=>{
    const short=s.label.length>38?'…'+s.label.slice(-36):s.label;
    if(i<drillStack.length-1)
      return `<span onclick="drillUp(${i})" title="${esc(s.label)}">${esc(short)}</span> /`;
    return `<strong title="${esc(s.label)}">${esc(short)}</strong>`;
  }).join(' ');
}

async function loadDrill(path){
  renderBreadcrumb();
  const body=document.getElementById('drill-body');
  body.innerHTML=`<div class="drill-loading"><div class="spinner" style="width:24px;height:24px;border-width:2px;margin:0 auto 10px"></div>${esc(t().drill.loading)}</div>`;
  try{
    const r=await fetch('/api/browse?path='+encodeURIComponent(path));
    const d=await r.json();
    if(d.error){body.innerHTML=`<div class="drill-err">⚠️ ${esc(d.error)}</div>`;return;}
    if(!d.items.length){body.innerHTML=`<div class="drill-empty">${esc(t().drill.empty)}</div>`;return;}
    body.innerHTML='';
    d.items.forEach(item=>{
      const row=document.createElement('div');
      row.className='drill-row';
      const icon=item.is_dir?'📁':'📄';
      const canDelete=item.deletable!==false;
      const deleteReason=getDeleteReason(item);
      row.innerHTML=`
        <span class="drill-icon">${icon}</span>
        <span class="drill-name${item.is_hidden?' hidden':''}" title="${esc(item.path)}">${esc(item.name)}</span>
        <div class="drill-bar-wrap"><div class="drill-bar-fill" style="width:${item.pct}%"></div></div>
        <span class="drill-size">${esc(item.size_formatted)}</span>
        <div class="drill-actions">
          <button class="drill-open-btn" onclick="openInFinder('${esc(item.path)}',event)" title="${esc(t().drill.openTitle)}">📂</button>
          <button class="drill-del-btn" data-path="${esc(item.path)}" data-deletable="${canDelete?'1':'0'}" data-reason-zh="${esc(item.delete_reason||'')}" data-reason-en="${esc(item.delete_reason_en||'')}" title="${esc(canDelete?t().card.delete:deleteReason)}" onclick="askDeletePath(this,event)" ${canDelete?'':'disabled'}>🗑</button>
        </div>`;
      if(item.is_dir){
        row.querySelector('.drill-name').onclick=(e)=>{e.stopPropagation();drillInto(item.path, item.name);};
        row.querySelector('.drill-icon').onclick=(e)=>{e.stopPropagation();drillInto(item.path, item.name);};
        row.ondblclick=(e)=>{e.stopPropagation();drillInto(item.path, item.name);};
      }
      body.appendChild(row);
    });
  }catch(e){body.innerHTML=`<div class="drill-err">${esc(t().drill.requestFailed)}${esc(e.message)}</div>`;}
}

function askDeletePath(btn, e){
  if(e) e.stopPropagation();
  if(btn.dataset.deletable==='0'){
    const reason=getButtonDeleteReason(btn);
    if(reason) showToast(reason);
    return;
  }
  // reuse modal, but without a card button reference
  const path=btn.dataset.path;
  pendingDelete={path, btn:null, fromDrill:true};
  document.getElementById('modal-path').textContent=path;
  document.getElementById('modal-warn').style.display='none';
  document.getElementById('modal').style.display='flex';
}

function showToast(msg){
  const t=document.getElementById('toast');t.textContent=msg;t.classList.add('show');
  setTimeout(()=>t.classList.remove('show'),3000);
}
function esc(s){return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');}
function fmtBytes(n){if(!n)return'0 B';if(n<1024**2)return(n/1024).toFixed(0)+' KB';if(n<1024**3)return(n/1024**2).toFixed(1)+' MB';return(n/1024**3).toFixed(2)+' GB';}
setLanguage(localStorage.getItem('mac-disk-analyzer-lang')||'zh');
</script>
</body>
</html>
"""
