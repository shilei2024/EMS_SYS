<template>
  <div class="about-page">
    <!-- 顶部导航 -->
    <header class="site-header">
      <div class="container header-content">
        <div class="logo">
          <NuxtLink to="/">
            <span class="logo-text">元器件商城</span>
          </NuxtLink>
        </div>

        <nav class="main-nav">
          <NuxtLink to="/">首页</NuxtLink>
          <NuxtLink to="/products">产品中心</NuxtLink>
          <NuxtLink to="/about">关于我们</NuxtLink>
          <NuxtLink to="/contact">联系我们</NuxtLink>
        </nav>

        <div class="header-actions">
          <NuxtLink to="/login" class="btn btn-outline">登录</NuxtLink>
          <NuxtLink to="/register" class="btn btn-primary">注册</NuxtLink>
        </div>
      </div>
    </header>

    <!-- 关于我们 Hero -->
    <section class="about-hero">
      <div class="container">
        <h1>关于我们</h1>
        <p>专业的电子元器件供应商，致力于为客户提供优质的产品和服务</p>
      </div>
    </section>

    <!-- 公司介绍 -->
    <section class="company-intro">
      <div class="container">
        <div class="intro-content">
          <div class="intro-text">
            <h2>公司简介</h2>
            <p>
              元器件商城成立于 2020 年，是一家专注于电子元器件销售的电子商务平台。
              我们与全球各大知名厂商建立了长期稳定的合作关系，包括 STMicroelectronics、
              Texas Instruments、NXP、Infineon、Microchip 等。
            </p>
            <p>
              公司拥有超过 10,000 种产品型号，涵盖 MCU、存储器、传感器、电源管理芯片、
              模拟器件、无线模块等多个品类。我们致力于为客户提供一站式采购解决方案，
              以优质的产品、合理的价格和完善的服务赢得客户的信赖。
            </p>
          </div>
          <div class="intro-image">
            <div class="image-placeholder">公司图片</div>
          </div>
        </div>
      </div>
    </section>

    <!-- 核心优势 -->
    <section class="advantages-section">
      <div class="container">
        <h2 class="section-title">我们的优势</h2>
        <div class="advantages-grid">
          <div class="advantage-card">
            <div class="advantage-icon">🏆</div>
            <h3>品质保证</h3>
            <p>所有产品均来自原厂或授权代理商，100% 正品保证</p>
          </div>
          <div class="advantage-card">
            <div class="advantage-icon">💰</div>
            <h3>价格优势</h3>
            <p>规模化采购，为客户提供最具竞争力的价格</p>
          </div>
          <div class="advantage-card">
            <div class="advantage-icon">📦</div>
            <h3>现货库存</h3>
            <p>常备库存超过 100 万件，快速发货</p>
          </div>
          <div class="advantage-card">
            <div class="advantage-icon">🚚</div>
            <h3>快速配送</h3>
            <p>与多家物流公司合作，确保货物安全快速送达</p>
          </div>
          <div class="advantage-card">
            <div class="advantage-icon">🔧</div>
            <h3>技术支持</h3>
            <p>专业的 FAE 团队，提供选型和技术咨询服务</p>
          </div>
          <div class="advantage-card">
            <div class="advantage-icon">💼</div>
            <h3>售后服务</h3>
            <p>完善的售后服务体系，解决客户后顾之忧</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 数据统计 -->
    <section class="stats-section">
      <div class="container">
        <div class="stats-grid">
          <div class="stat-item">
            <span class="stat-value">10,000+</span>
            <span class="stat-label">产品型号</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">5,000+</span>
            <span class="stat-label">合作客户</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">50+</span>
            <span class="stat-label">合作品牌</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">99%</span>
            <span class="stat-label">客户满意度</span>
          </div>
        </div>
      </div>
    </section>

    <!-- 合作品牌 -->
    <section class="brands-section">
      <div class="container">
        <h2 class="section-title">合作品牌</h2>
        <div class="brands-grid">
          <div class="brand-item">STMicroelectronics</div>
          <div class="brand-item">Texas Instruments</div>
          <div class="brand-item">NXP</div>
          <div class="brand-item">Infineon</div>
          <div class="brand-item">Microchip</div>
          <div class="brand-item">Espressif</div>
          <div class="brand-item">Analog Devices</div>
          <div class="brand-item">ON Semiconductor</div>
        </div>
      </div>
    </section>

    <!-- 底部 -->
    <footer class="site-footer">
      <div class="container">
        <div class="footer-content">
          <div class="footer-section">
            <h4>关于我们</h4>
            <p>专业的电子元器件供应商</p>
          </div>
          <div class="footer-section">
            <h4>快速链接</h4>
            <ul>
              <li><NuxtLink to="/products">产品中心</NuxtLink></li>
              <li><NuxtLink to="/about">关于我们</NuxtLink></li>
            </ul>
          </div>
          <div class="footer-section">
            <h4>联系方式</h4>
            <p>电话：400-xxx-xxxx</p>
            <p>邮箱：info@example.com</p>
          </div>
        </div>
        <div class="footer-bottom">
          <p>&copy; 2026 元器件商城。All rights reserved.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
// SEO
useHead({
  title: '关于我们 - 元器件商城',
  meta: [
    { name: 'description', content: '了解元器件商城，专业的电子元器件供应商' }
  ]
})
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 顶部导航 */
.site-header {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
}

.logo-text {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}

.main-nav {
  display: flex;
  gap: 30px;
}

.main-nav a {
  color: #333;
  text-decoration: none;
  font-size: 16px;
}

.header-actions {
  display: flex;
  gap: 15px;
}

.btn {
  padding: 8px 20px;
  border-radius: 4px;
  text-decoration: none;
  font-size: 14px;
  cursor: pointer;
}

.btn-outline {
  border: 1px solid #409eff;
  color: #409eff;
  background: white;
}

.btn-primary {
  background: #409eff;
  color: white;
  border: none;
}

/* About Hero */
.about-hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 80px 0;
  text-align: center;
}

.about-hero h1 {
  font-size: 48px;
  margin-bottom: 15px;
}

.about-hero p {
  font-size: 18px;
  opacity: 0.9;
}

/* 公司介绍 */
.company-intro {
  padding: 80px 0;
}

.intro-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 50px;
  align-items: center;
}

.intro-text h2 {
  font-size: 32px;
  color: #333;
  margin-bottom: 25px;
}

.intro-text p {
  font-size: 16px;
  color: #666;
  line-height: 1.8;
  margin-bottom: 20px;
}

.intro-image {
  height: 350px;
  background: #f5f7fa;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-placeholder {
  color: #999;
  font-size: 16px;
}

/* 优势部分 */
.advantages-section {
  padding: 80px 0;
  background: #f5f7fa;
}

.section-title {
  text-align: center;
  font-size: 36px;
  color: #333;
  margin-bottom: 50px;
}

.advantages-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 30px;
}

.advantage-card {
  background: white;
  padding: 30px;
  border-radius: 8px;
  text-align: center;
  transition: transform 0.3s, box-shadow 0.3s;
}

.advantage-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.advantage-icon {
  font-size: 50px;
  margin-bottom: 20px;
}

.advantage-card h3 {
  font-size: 20px;
  color: #333;
  margin-bottom: 15px;
}

.advantage-card p {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
}

/* 数据统计 */
.stats-section {
  padding: 80px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 30px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 48px;
  font-weight: bold;
  margin-bottom: 10px;
}

.stat-label {
  font-size: 16px;
  opacity: 0.9;
}

/* 合作品牌 */
.brands-section {
  padding: 80px 0;
}

.brands-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.brand-item {
  padding: 30px;
  background: #f5f7fa;
  border-radius: 8px;
  text-align: center;
  font-size: 18px;
  color: #666;
  font-weight: 500;
}

/* 底部 */
.site-footer {
  background: #2c3e50;
  color: white;
  padding: 40px 0 20px;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
  margin-bottom: 30px;
}

.footer-section h4 {
  font-size: 18px;
  margin-bottom: 15px;
}

.footer-section p {
  font-size: 14px;
  line-height: 1.8;
  opacity: 0.8;
}

.footer-section ul {
  list-style: none;
  padding: 0;
}

.footer-section ul li {
  margin-bottom: 10px;
}

.footer-section a {
  color: white;
  text-decoration: none;
  opacity: 0.8;
}

.footer-bottom {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.footer-bottom p {
  font-size: 14px;
  opacity: 0.6;
}

/* 响应式 */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .intro-content {
    grid-template-columns: 1fr;
  }
}
</style>
