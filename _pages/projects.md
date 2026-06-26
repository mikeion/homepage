---
layout: default
title: "Projects"
permalink: /projects/
---

<section class="projects">

<h1>Projects</h1>

<p>Things I've built outside of papers — games, tools, and prototypes. The research and the side projects are more connected than they look: a lot of what I think about in studying learning and conversation shows up in how I approach game design.</p>

<h2>Games</h2>

<div class="project">
  <h3>Tide &amp; Tower</h3>
  <div class="meta">Vocabulary game · Godot 4 · Complete</div>
  <p>A hangman variant built for a friend. Instead of a gallows, a sandcastle sits on the beach; each wrong guess brings the tide closer until it washes over. Runs in both English and Haitian Creole, with hints written in Creole for the Creole mode — built after learning the friend it was made for teaches remotely at a school in Haiti. The Godot project is named Kastèl Sab: sand castle in Haitian Creole.</p>
</div>

<div class="project">
  <h3>Gin &amp; Tonic</h3>
  <div class="meta">Card game roguelike · TypeScript / Phaser · Godot port in progress</div>
  <p>A roguelike where you fight enemies by playing Gin Rummy. Melds deal damage — sets multiply rank by card count, runs deal the sum — and relics collected between fights modify your playstyle. Inspired by Balatro and Slay the Spire. The web version runs in Phaser; I'm mid-way through evaluating a port to Godot 4, with the decision gating on whether GDScript can run a backtracking meld-finding algorithm in under 50ms for 10-card hands.</p>
</div>

<div class="project">
  <h3>Pixel Pickaxe</h3>
  <div class="meta">Roguelite tap-clicker · Godot 4 · In development</div>
  <p>A tap-clicker organized around discrete 5-minute mining expeditions instead of an infinite treadmill. Before each run you pick a loadout — pickaxe, three miners, two active skills — then race to beat a cave boss before the timer runs out. 12 themed caves to clear, roughly 30 runs to finish the game. The design argument: idle game research shows completion and power are the top player motivators, and most clickers only deliver power. Part of the Tideline Games project.</p>
</div>

<div class="project">
  <h3>Menderbloom</h3>
  <div class="meta">Cozy idle / incremental · Web · In development</div>
  <p>An incremental game about healing a dying world one terrarium at a time. You tend plants, exploit seasonal synergies, and prestige by releasing a terrarium to restore a region — 100 regions in total. The central design problem for the genre: how do you make something that feels like a living garden rather than a spreadsheet with plant names?</p>
</div>

<h2>Tools</h2>

<div class="project">
  <h3>Life Calendar</h3>
  <div class="meta">Web app · Next.js · TypeScript · Prisma</div>
  <p>A "Your Life in Weeks" visualization — your entire life rendered as a grid of weeks, color-coded by era or activity. Built after reading Tim Urban's framing that most people have around 4,000 weeks; I wanted a version with a personal data layer and reflection prompts attached to specific weeks rather than just a static poster.</p>
</div>

<div class="project">
  <h3>Learning Through Technical Interviews</h3>
  <div class="meta">2025–present · co-PI · Academic Innovation Fund, University of Michigan ($12,435)</div>
  <p>An AI-powered technical-interview practice platform for data science students. Real-time assessment against standardized rubrics for technical communication, code comprehension, strategic thinking, and coding creativity. Built on the adaptive-assessment framework from <a href="https://proceedings.mlr.press/v273/ion25a.html">Ion et al. 2025 (iRAISE)</a>.</p>
</div>

<div class="project">
  <h3>MathMentorDB</h3>
  <div class="meta">Research infrastructure · 200K+ conversations, 5.5M messages</div>
  <p>Structured dataset built from a large public mathematics Discord server, transformed into conversation-level units with participant roles, timestamps, and channel metadata. Underlies most of my recent empirical work on tutoring discourse.</p>
</div>

</section>
