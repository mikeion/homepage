---
layout: default
title: "Publications"
permalink: /publications/
---

<div class="publications">

{% for group in site.data.papers %}
<h3>{{ group.year }}</h3>
<ul>
{% for paper in group.items %}  <li><span class="tag tag-{{ paper.type }}">{{ paper.type }}</span> {{ paper.entry }}{% if paper.summary %}
    <details class="paper-summary"><summary>Summary</summary><p class="blurb">{{ paper.summary | strip }}</p></details>{% endif %}
  </li>
{% endfor %}</ul>

{% endfor %}
</div>
