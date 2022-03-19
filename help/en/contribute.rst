Contribute to dupeGuru
======================

dupeGuru was started as shareware (thus proprietary) so it doesn't have a legacy of
community-building. It's `been open source`_ for a while now and, although I've ("I" being Virgil
Dupras, author of the software) always wanted to have people other than me working on dupeGuru, I've
failed at attracting them.

Since the end of 2013, I've been putting a lot of efforts into dupeGuru's
:doc:`developer documentation </developer/index>` and I'm more serious about my commitment to create
a community around this project.

So, whatever your skills, if you're interested in contributing to dupeGuru, please do so. Normally,
this documentation should be enough to get you started, but if it isn't, then **please**,
open a discussion at https://github.com/arsenetar/dupeguru/discussions.  If there's any situation where you'd
wish to contribute but some doubt you're having prevent you from going forward, please contact me.
I'd much prefer to spend the time figuring out with you whether (and how) you can contribute than
taking the chance of missing that opportunity.

Development process
-------------------

* `Source code repository`_
* `Issue Tracker`_
* `Issue labels meaning`_

dupeGuru's source code is on Github and thus managed in a Git repository. At all times, you should
be able to build from source a fresh checkout of the ``master`` branch using instructions from the
``README.md`` file at the root of this project. If you can't, it's a bug. Please report it.

``master`` is the main development branch, and thus represents what going to be included in the
next feature release. When needed, we create maintenance branches for bugfixes of the current
feature release.

When implementing a big feature, it's possible that it gets its own branch until
it's stable enough to merge into ``master``.

Every release is tagged, the tag name containing the edition (for old versions) and its version.
For example, release 6.6.0 of dupeGuru ME is tagged ``me6.6.0``. Newer releases are tagged only
with the version number (because editions don't exist anymore), for example ``4.0.0``.

Once you're past building the software, the :doc:`developer documentation </developer/index>` should
be enough to get you started with actual development. Then again, proper documentation is a very
difficult task and, in the case of dupeGuru, this documentation was practically nonexistent until
late in the project, so it's still lacking.

However, I'm committed to fix this situation, so if you're in a situation where you lack proper
documentation to figure something out about this code, please contact me.

Tasks for non-developers
------------------------

**Create and comment issues**. The single most useful way for a user who is not a developer to
contribute to a software project is by thoroughly documenting a bug or a feature request. Most of
the time, what we get as developers are emails like "the app crashes" and we spend a lot of time
trying to figure out the cause of that bug. By properly describing the nature and context of a crash
(we learn to do that with experience as a user who reports bugs), you help developers so immensely,
you have no idea.

It's the same thing with feature requests. Description of a feature request, when thoughts have
already been given to how such a feature would fit in the current design, are precious to developers
and help them figure out a clear roadmap for the project.

So, even if you're not a developer, you can always open a Github account and create/comment issues.
Your contribution will be much appreciated.

**Documentation**. This is a bit trickier because dupeGuru's documentation is written with a rather
complex markup language, `Sphinx`_ (based on `reST`_). To properly work within the documentation,
you have to know that language. I don't think that learning this language is outside the realm of
possibility for a non-developer, but it might be a daunting task.

That being said, if it's a minor modification to the documentation, nothing stops you from opening
an issue (there's a label for documentation issues, so this kind of issue is relevant to the
tracker) describing the change you propose to make and I'll be happy to make the change myself (if
relevant, of course).

Even if it's a bigger contribution to the documentation you want to make, I probably wouldn't mind
doing the formatting myself. But in that case, it's better to contact me first to make sure that we
agree on what should be added to the documentation.

**Translation**. Creating or improving an existing translation is a very good way to contribute to
dupeGuru. For more information about how to do that, you can refer to the `translator guide`_.

.. _been open source: https://www.hardcoded.net/articles/free-as-in-speech-fair-as-in-trade
.. _Source code repository: https://github.com/arsenetar/dupeguru
.. _Issue Tracker: https://github.com/arsenetar/issues
.. _Issue labels meaning: https://github.com/arsenetar/wiki/issue-labels
.. _Sphinx: http://sphinx-doc.org/
.. _reST: http://en.wikipedia.org/wiki/ReStructuredText
.. _translator guide: https://github.com/arsenetar/wiki/Translator-Guide
