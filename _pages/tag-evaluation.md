---
layout: default
title: "Posts tagged evaluation"
permalink: /blog/tags/evaluation/
---

<section class="blog">

<h1>Posts tagged <span class="wtag">evaluation</span></h1>

<p><a href="{{ '/blog/' | relative_url }}">← all posts</a></p>

<ul class="blog-index">
  {% for post in site.tags.evaluation %}
  <li>
    <div class="post-meta">
      <time datetime="{{ post.date | date_to_xmlschema }}">{{ post.date | date: "%b %-d, %Y" }}</time>{% if post.tags and post.tags.size > 0 %} · {% for tag in post.tags %}<a class="wtag" href="{{ '/blog/tags/' | append: tag | append: '/' | relative_url }}">{{ tag }}</a>{% unless forloop.last %} {% endunless %}{% endfor %}{% endif %}
    </div>
    <a class="post-title" href="{{ post.url | relative_url }}">{{ post.title }}</a>
    {% if post.description %}<p class="post-excerpt">{{ post.description }}</p>{% endif %}
  </li>
  {% endfor %}
</ul>

</section>
