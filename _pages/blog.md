---
layout: default
title: "Blog"
permalink: /blog/
---

<section class="blog">

<h1>Blog</h1>

<p>Short-form posts on LLM evaluation methodology, measurement in education, and whatever I'm currently thinking through. Looking for longer, structured write-ups instead? See <a href="{{ '/notes/' | relative_url }}">notes</a>.</p>

{% if site.posts.size > 0 %}
<ul class="blog-index">
  {% for post in site.posts %}
  <li>
    <div class="post-meta">
      <time datetime="{{ post.date | date_to_xmlschema }}">{{ post.date | date: "%b %-d, %Y" }}</time>{% if post.tags and post.tags.size > 0 %} · {% for tag in post.tags %}<a class="wtag" href="{{ '/blog/tags/' | append: tag | append: '/' | relative_url }}">{{ tag }}</a>{% unless forloop.last %} {% endunless %}{% endfor %}{% endif %}
    </div>
    <a class="post-title" href="{{ post.url | relative_url }}">{{ post.title }}</a>
    {% if post.description %}<p class="post-excerpt">{{ post.description }}</p>{% endif %}
  </li>
  {% endfor %}
</ul>
{% else %}
<p><em>First post coming soon.</em></p>
{% endif %}

</section>
