#!/usr/bin/env node
import chalk from 'chalk';
import inquirer from 'inquirer';
import figlet from 'figlet';
import gradient from 'gradient-string';
import Table from 'cli-table3';
import boxen from 'boxen';
import { promises as fs } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ASSESSMENTS_DIR = join(__dirname, 'assessments');

// ─── Rubric ──────────────────────────────────────────────────────────────────

const CATEGORIES = [
  {
    id: 1,
    name: 'Timing',
    question: 'Does the timing feel suspicious or too convenient — coinciding with elections, legislation, economic events, or other crises that it distracts from?',
    hint: '1 = Timing seems organic  |  5 = Timing is eerily convenient',
  },
  {
    id: 2,
    name: 'Emotional Manipulation',
    question: 'Does the story provoke intense fear, outrage, or guilt without solid, verifiable evidence to justify that emotional response?',
    hint: '1 = Measured, evidence-based  |  5 = Pure emotional trigger, no substance',
  },
  {
    id: 3,
    name: 'Uniform Messaging',
    question: 'Are identical key phrases, framing, or talking points repeated across all major media outlets simultaneously, as if from a single script?',
    hint: '1 = Diverse coverage  |  5 = Word-for-word identical across outlets',
  },
  {
    id: 4,
    name: 'Missing Information',
    question: 'Are critical alternative viewpoints, contradictory data, or key context deliberately excluded from all mainstream coverage?',
    hint: '1 = Full picture presented  |  5 = Glaring omissions, dissent invisible',
  },
  {
    id: 5,
    name: 'Simplistic Narratives',
    question: 'Is a complex situation reduced to a "good vs. evil" or "us vs. them" framework that leaves no room for nuance?',
    hint: '1 = Nuanced coverage  |  5 = Pure black-and-white moral framing',
  },
  {
    id: 6,
    name: 'Tribal Division',
    question: 'Does the story deliberately inflame divisions along political, racial, religious, or class lines — pitting groups against each other?',
    hint: '1 = No tribal framing  |  5 = Aggressively stokes group conflict',
  },
  {
    id: 7,
    name: 'Authority Overload',
    question: 'Are an overwhelming number of "experts," officials, or institutions cited in lockstep to shut down questioning rather than inform?',
    hint: '1 = Balanced sourcing  |  5 = Saturated with authority to silence dissent',
  },
  {
    id: 8,
    name: 'Call for Urgent Action',
    question: 'Is there intense pressure to act immediately — surrendering rights, accepting restrictions, or making decisions before you can think critically?',
    hint: '1 = No urgency manufactured  |  5 = "Act now or catastrophe" framing',
  },
  {
    id: 9,
    name: 'Overuse of Novelty',
    question: 'Is the event presented as completely unprecedented — something the world has never seen — in a way that paralyzes historical comparison?',
    hint: '1 = Grounded in context  |  5 = "Never before in history" used to isolate',
  },
  {
    id: 10,
    name: 'Financial / Political Gain',
    question: 'Can you identify clear financial or political beneficiaries who gain power, profit, or policy wins from this event or narrative?',
    hint: '1 = No obvious beneficiaries  |  5 = Direct, traceable gain for known actors',
  },
  {
    id: 11,
    name: 'Suppression of Dissent',
    question: 'Are people who question the narrative being silenced, deplatformed, ridiculed, or labeled as dangerous — rather than debated?',
    hint: '1 = Open debate tolerated  |  5 = Questioners destroyed or censored',
  },
  {
    id: 12,
    name: 'False Dilemmas',
    question: 'Is the public presented with only two options — both of which serve the same agenda — while other paths are never discussed?',
    hint: '1 = Multiple options presented  |  5 = Binary choice, both bad for you',
  },
  {
    id: 13,
    name: 'Inconsistent Details',
    question: 'Do the official facts, timelines, or evidence change frequently in ways that are never satisfactorily explained?',
    hint: '1 = Story is consistent  |  5 = Story shifts constantly, no accountability',
  },
  {
    id: 14,
    name: 'Prepackaged Solutions',
    question: 'Did the solution — a law, product, policy, or treaty — appear suspiciously fast, as if it had been prepared in advance of the crisis?',
    hint: '1 = Response developed organically  |  5 = Solution was clearly pre-written',
  },
  {
    id: 15,
    name: 'Unverifiable Claims',
    question: 'Are key claims based on classified intel, anonymous sources, or evidence the public can never independently examine?',
    hint: '1 = Evidence is open and verifiable  |  5 = "Trust us" — nothing can be checked',
  },
  {
    id: 16,
    name: 'Hero / Villain Construction',
    question: 'Have specific individuals been elevated as perfect heroes or demonized as pure villains in ways that feel scripted or theatrical?',
    hint: '1 = People portrayed with complexity  |  5 = Cartoonish archetypes, no nuance',
  },
  {
    id: 17,
    name: 'Rapid Memory-Holing',
    question: 'Did contradictory evidence, early reports, or the story itself vanish from coverage without explanation once it served its purpose?',
    hint: '1 = Story followed up thoroughly  |  5 = Disappeared overnight, never resolved',
  },
  {
    id: 18,
    name: 'Shifting Explanations',
    question: 'Did the official explanation change dramatically over time — with earlier versions scrubbed — and was no one held accountable for the errors?',
    hint: '1 = Stable, consistent account  |  5 = Constantly revised, old versions erased',
  },
  {
    id: 19,
    name: 'Selective Evidence Presentation',
    question: 'Is only evidence that supports the official narrative highlighted, while contradictory data is buried, dismissed, or ridiculed?',
    hint: '1 = All evidence fairly weighed  |  5 = Cherry-picked, counter-evidence attacked',
  },
  {
    id: 20,
    name: 'Beneficiary Analysis',
    question: 'When you ask "who benefits from the public believing this narrative?", do powerful institutional, governmental, or corporate actors emerge as clear winners?',
    hint: '1 = No concentrated benefit  |  5 = Same small group gains on every axis',
  },
];

// ─── Scoring ─────────────────────────────────────────────────────────────────

function getVerdict(total) {
  if (total <= 40) {
    return {
      label: 'LOW LIKELIHOOD',
      color: chalk.green,
      bar: chalk.green,
      description: 'Largely organic. Minimal coordination signals detected. Maintain healthy skepticism but no strong psyop indicators.',
    };
  } else if (total <= 60) {
    return {
      label: 'MODERATE LIKELIHOOD',
      color: chalk.yellow,
      bar: chalk.yellow,
      description: 'Mixed signals. Some engineered elements may be present. Dig deeper before forming conclusions.',
    };
  } else if (total <= 80) {
    return {
      label: 'STRONG LIKELIHOOD',
      color: chalk.hex('#FF8C00'),
      bar: chalk.hex('#FF8C00'),
      description: 'Strong indicators of narrative shaping. Multiple coordination patterns detected. Treat with significant skepticism.',
    };
  } else {
    return {
      label: 'OVERWHELMING SIGNS',
      color: chalk.red,
      bar: chalk.red,
      description: 'Heavy coordinated information operation. Nearly every psyop marker is present. Do not accept this narrative at face value.',
    };
  }
}

function renderProgressBar(score, max = 5, width = 20) {
  const filled = Math.round((score / max) * width);
  const empty = width - filled;
  let color;
  if (score <= 2) color = chalk.green;
  else if (score === 3) color = chalk.yellow;
  else if (score === 4) color = chalk.hex('#FF8C00');
  else color = chalk.red;
  return color('█'.repeat(filled)) + chalk.gray('░'.repeat(empty));
}

function renderTotalBar(total, max = 100, width = 40) {
  const verdict = getVerdict(total);
  const filled = Math.round((total / max) * width);
  const empty = width - filled;
  return verdict.bar('█'.repeat(filled)) + chalk.gray('░'.repeat(empty));
}

// ─── File output ──────────────────────────────────────────────────────────────

function slugify(str) {
  return str
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .trim()
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .slice(0, 80);
}

async function saveAssessment(eventName, scores, notes, total, verdict) {
  await fs.mkdir(ASSESSMENTS_DIR, { recursive: true });

  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
  const slug = slugify(eventName);
  const filename = `${slug}_${timestamp}.md`;
  const filepath = join(ASSESSMENTS_DIR, filename);

  const lines = [
    `# NCI Engineered Reality Scorecard`,
    ``,
    `**Event:** ${eventName}`,
    `**Date:** ${new Date().toLocaleString()}`,
    `**Total Score:** ${total} / 100`,
    `**Verdict:** ${verdict.label}`,
    ``,
    `---`,
    ``,
    `## Verdict`,
    ``,
    `> ${verdict.description}`,
    ``,
    `---`,
    ``,
    `## Category Scores`,
    ``,
    `| # | Category | Score | Notes |`,
    `|---|----------|-------|-------|`,
    ...CATEGORIES.map((cat, i) => {
      const score = scores[i];
      const note = notes[i] || '';
      return `| ${cat.id} | ${cat.name} | ${score}/5 | ${note} |`;
    }),
    ``,
    `---`,
    ``,
    `## Score Interpretation`,
    ``,
    `| Range | Likelihood |`,
    `|-------|-----------|`,
    `| 20–40 | Low — largely organic |`,
    `| 41–60 | Moderate — some engineered elements |`,
    `| 61–80 | Strong — narrative shaping likely |`,
    `| 81–100 | Overwhelming — coordinated information operation |`,
    ``,
    `---`,
    ``,
    `*Generated by the NCI Engineered Reality Scoring System CLI*`,
  ];

  await fs.writeFile(filepath, lines.join('\n'), 'utf8');
  return filepath;
}

// ─── UI helpers ───────────────────────────────────────────────────────────────

function clearLine() {
  process.stdout.write('\n');
}

function printHeader() {
  console.clear();
  const title = figlet.textSync('PSYOP\nSCORECARD', {
    font: 'Big',
    horizontalLayout: 'default',
  });
  console.log(gradient(['#ff0000', '#ff6600', '#ffaa00'])(title));
  console.log(
    chalk.gray('  ') +
    chalk.dim('NCI Engineered Reality Scoring System  ·  Chase Hughes') +
    '\n'
  );
}

function printSectionDivider(label) {
  const line = '─'.repeat(60);
  console.log('\n' + chalk.dim(line));
  if (label) console.log(chalk.bold.cyan(`  ${label}`));
  console.log(chalk.dim(line) + '\n');
}

function printCategoryHeader(cat) {
  console.log(
    chalk.bold.white(`  [${cat.id}/20] `) +
    chalk.bold.cyan(cat.name.toUpperCase())
  );
  console.log(chalk.dim('  ' + '─'.repeat(56)));
}

// ─── Main ─────────────────────────────────────────────────────────────────────

async function main() {
  printHeader();

  console.log(
    boxen(
      chalk.white.bold('Welcome to the NCI Engineered Reality Scoring System\n') +
      chalk.gray(
        'Score a news event or potential psyop across 20 categories.\n' +
        'Each category is rated 1–5. Total score: 20–100.\n\n' +
        chalk.green('1–2') + chalk.gray(' = Low signal  ') +
        chalk.yellow('3') + chalk.gray(' = Moderate  ') +
        chalk.hex('#FF8C00')('4') + chalk.gray(' = High  ') +
        chalk.red('5') + chalk.gray(' = Overwhelming')
      ),
      {
        padding: 1,
        margin: { top: 0, bottom: 1, left: 2, right: 2 },
        borderStyle: 'round',
        borderColor: 'cyan',
      }
    )
  );

  // ── Event name ──
  const { eventName } = await inquirer.prompt([
    {
      type: 'input',
      name: 'eventName',
      message: chalk.bold.yellow('Name the news event or potential psyop:'),
      validate: (v) => v.trim().length > 0 || 'Please enter a name.',
    },
  ]);

  clearLine();
  console.log(
    chalk.bold('  Assessing: ') + chalk.cyan.bold(eventName.trim()) + '\n'
  );

  const scores = [];
  const notes = [];

  printSectionDivider('CATEGORY ASSESSMENT  (score each 1–5, add optional notes)');

  for (let i = 0; i < CATEGORIES.length; i++) {
    const cat = CATEGORIES[i];

    printCategoryHeader(cat);
    console.log(chalk.white('  ' + cat.question));
    console.log(chalk.dim('  ' + cat.hint));
    clearLine();

    const answers = await inquirer.prompt([
      {
        type: 'list',
        name: 'score',
        message: chalk.bold(`  Score for "${cat.name}":`),
        choices: [
          { name: chalk.green('1 — Not present'), value: 1 },
          { name: chalk.green('2 — Slightly present'), value: 2 },
          { name: chalk.yellow('3 — Moderately present'), value: 3 },
          { name: chalk.hex('#FF8C00')('4 — Strongly present'), value: 4 },
          { name: chalk.red('5 — Overwhelmingly present'), value: 5 },
        ],
        pageSize: 5,
      },
      {
        type: 'input',
        name: 'note',
        message: chalk.dim('  Note (optional, press Enter to skip):'),
      },
    ]);

    scores.push(answers.score);
    notes.push(answers.note.trim());

    const bar = renderProgressBar(answers.score);
    console.log(
      chalk.dim('\n  Score: ') + bar + chalk.dim(` ${answers.score}/5\n`)
    );
  }

  // ── Results ──
  const total = scores.reduce((a, b) => a + b, 0);
  const verdict = getVerdict(total);

  printSectionDivider('RESULTS');

  // Score table
  const table = new Table({
    head: [
      chalk.bold.cyan('#'),
      chalk.bold.cyan('Category'),
      chalk.bold.cyan('Score'),
      chalk.bold.cyan('Bar'),
      chalk.bold.cyan('Notes'),
    ],
    colWidths: [4, 28, 7, 24, 30],
    style: { border: ['gray'] },
    wordWrap: true,
  });

  for (let i = 0; i < CATEGORIES.length; i++) {
    const score = scores[i];
    let scoreStr;
    if (score <= 2) scoreStr = chalk.green(`${score}/5`);
    else if (score === 3) scoreStr = chalk.yellow(`${score}/5`);
    else if (score === 4) scoreStr = chalk.hex('#FF8C00')(`${score}/5`);
    else scoreStr = chalk.red(`${score}/5`);

    table.push([
      chalk.dim(String(CATEGORIES[i].id)),
      CATEGORIES[i].name,
      scoreStr,
      renderProgressBar(score),
      chalk.dim(notes[i] || '—'),
    ]);
  }

  console.log(table.toString());

  // Total score
  clearLine();
  const totalBar = renderTotalBar(total);
  console.log(chalk.bold('  Total Score: ') + verdict.color.bold(`${total}/100`));
  console.log(chalk.dim('  ') + totalBar + chalk.dim(` ${total}/100`));
  clearLine();

  // Verdict box
  console.log(
    boxen(
      verdict.color.bold(`  ${verdict.label}\n\n`) +
      chalk.white('  ' + verdict.description),
      {
        padding: 1,
        margin: { top: 0, bottom: 1, left: 2, right: 2 },
        borderStyle: 'double',
        borderColor: total > 60 ? 'red' : total > 40 ? 'yellow' : 'green',
        title: chalk.bold('VERDICT'),
        titleAlignment: 'center',
      }
    )
  );

  // Save
  const filepath = await saveAssessment(eventName.trim(), scores, notes, total, verdict);

  console.log(
    chalk.dim('  Assessment saved to: ') + chalk.cyan(filepath) + '\n'
  );
}

main().catch((err) => {
  if (err.name === 'ExitPromptError') {
    console.log('\n' + chalk.dim('  Assessment cancelled.') + '\n');
    process.exit(0);
  }
  console.error(chalk.red('Error: ' + err.message));
  process.exit(1);
});
