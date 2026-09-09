const pw = require('C:/Users/Admin/AppData/Local/Packages/PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0/LocalCache/local-packages/Python312/site-packages/playwright/driver/package');
const fs = require('fs');
const path = require('path');

const RAW_FILE = path.join(__dirname, 'data', 'raw_scraped.json');

async function crawlLeetCode(maxPages = 2, maxPosts = 15) {
  console.log('====================================================');
  console.log(' LeetCode Discuss Automated Playwright Scraper');
  console.log('====================================================');

  const browser = await pw.chromium.launch({
    headless: true,
    args: ['--disable-blink-features=AutomationControlled', '--no-sandbox']
  });

  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    viewport: { width: 1366, height: 768 }
  });

  const page = await context.newPage();
  await page.addInitScript(() => { delete Object.getPrototypeOf(navigator).webdriver; });

  let capturedArticles = [];

  page.on('response', async res => {
    if (res.url().includes('graphql')) {
      try {
        const body = await res.json();
        const articles = body?.data?.ugcArticleDiscussionArticles?.edges;
        if (Array.isArray(articles) && articles.length > 0) {
          console.log(`[+] Intercepted ${articles.length} discuss articles.`);
          capturedArticles.push(...articles);
        }
      } catch (e) {}
    }
  });

  console.log('[*] Navigating to LeetCode Discuss...');
  await page.goto('https://leetcode.com/discuss/interview-experience?currentPage=1&orderBy=newest_to_oldest&query=Amazon', {
    waitUntil: 'domcontentloaded',
    timeout: 35000
  });
  await page.waitForTimeout(4000);

  // Filter Amazon posts
  const candidates = [];
  const seenIds = new Set();

  for (const edge of capturedArticles) {
    const node = edge.node;
    if (!node || seenIds.has(node.topicId)) continue;
    seenIds.add(node.topicId);

    const title = node.title || '';
    const summary = node.summary || '';
    const tags = (node.tags || []).map(t => t.name || '');
    const combined = `${title} ${summary} ${tags.join(' ')}`.toLowerCase();

    if (combined.includes('amazon') && (combined.includes('interview') || combined.includes('oa') || combined.includes('sde') || combined.includes('intern') || combined.includes('offer') || combined.includes('round'))) {
      candidates.push(node);
    }
  }

  console.log(`[*] Discovered ${candidates.length} relevant Amazon interview candidate topics.`);

  const scrapedDetails = [];
  const targetPosts = candidates.slice(0, maxPosts);

  for (let i = 0; i < targetPosts.length; i++) {
    const item = targetPosts[i];
    const postUrl = `https://leetcode.com/discuss/post/${item.topicId}/${item.slug || ''}/`;
    console.log(`[${i+1}/${targetPosts.length}] Scraping post #${item.topicId}: ${item.title.slice(0, 50)}...`);

    try {
      await page.goto(postUrl, { waitUntil: 'domcontentloaded', timeout: 25000 });
      await page.waitForTimeout(2500);

      const pageData = await page.evaluate(() => {
        const articleEl = document.querySelector('article') || document.querySelector('[data-layout="discussion-post"]') || document.querySelector('main');
        return { fullText: articleEl ? articleEl.innerText : document.body.innerText };
      });

      scrapedDetails.push({
        topicId: String(item.topicId),
        title: item.title,
        slug: item.slug,
        url: postUrl,
        author: item.author?.userName || item.author?.realName || 'Anonymous',
        createdAt: item.createdAt,
        votes: (item.reactions || []).find(r => r.reactionType === 'UPVOTE')?.count || 0,
        views: item.hitCount || 0,
        tags: (item.tags || []).map(t => t.name).filter(Boolean),
        summary: item.summary,
        fullText: pageData.fullText
      });
    } catch (err) {
      console.error(`[-] Error scraping ${postUrl}: ${err.message}`);
    }
  }

  await browser.close();

  fs.mkdirSync(path.dirname(RAW_FILE), { recursive: true });
  fs.writeFileSync(RAW_FILE, JSON.stringify(scrapedDetails, null, 2), 'utf-8');
  console.log(`[SUCCESS] Crawled ${scrapedDetails.length} posts and saved to ${RAW_FILE}`);
}

const postsLimit = parseInt(process.argv[2] || '10', 10);
crawlLeetCode(1, postsLimit);
