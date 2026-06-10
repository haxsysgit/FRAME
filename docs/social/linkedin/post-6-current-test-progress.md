# Post 6 -- current test progress

Target: LinkedIn
Status: paste-ready draft, no Markdown formatting in body
Series role: current test progress
Asset suggestion: ../assets/frame-post-6-test-progress-2800.png

---

Now the test progress part.

This is not a final result or some “FRAME is proven” claim. It is just where the current round landed while testing the v0.2.0 shape inside Frame Lab.

The current candidate averaged 4.35 out of 5 across three fixtures.

organize: 4.25 / 5
autopahe: 4.29 / 5
Pharmax: 4.50 / 5

The scores are useful, but the more important part is what the scores exposed.

The first thing i noticed is that simpler names helped immediately.

Names like Facts, Rules, Map, Expect, and Acts are boring in a good way. They are easy to explain. You do not need to teach someone a whole private language before they understand the shape.

The second thing is that the five parts started behaving more like one linked brain, not separate storage bins.

That matters because project truth is connected. A rule may point to a file. A test expectation may point to a fact. A run history entry may say which fact changed. If those links are clean, the project representation becomes more useful.

The third thing is Acts became more important than i first expected.

Acts is not baseline project truth. It is run history. It helps answer what happened, what changed, what was touched, what was checked, and what still needs attention.

That is a big deal when agents are generating more code than the developer can casually keep in their head.

Also, under this round of pressure, i did not need to add a new core block.

That part was important to me.

The structure got clearer mostly through naming, linking, and better placement, not by adding more and more fields.

The main weak spot is still proof discipline.

It is easy for an agent run to say something was checked when really it was only inspected. That difference matters, so Expect and Acts need to be strict about what actually passed versus what was only reasoned about.

Basically i am saying v0.2.0 looks promising, but the useful part is not the score.

The useful part is seeing where the structure holds, where it gets pressure, and where it still needs tightening.

#FRAME #agent
