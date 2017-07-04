---
draft: false
---

## Hacker News Security

If you find a security hole, please let us know at security@ycombinator.com. We try to respond (with fixes!) as soon as possible, and really appreciate the help.

Thanks to the following people who have discovered and responsibly disclosed security holes in Hacker News:

### 20170430: Michael Flaxman

    The minor version of bcrypt used for passwords was susceptible to a collision in some cases.

### 20170414: Blake Rand

    Links in comments were vulnerable to an IDN homograph attack.

### 20170315: Blake Rand

    The right-to-left override character could be used to obscure link text in comments.

### 20170301: Jaikishan Tulswani

    Logged-in users could bypass 'old password' form field.

### 20160217: Eric Tjossem

    Logout and login were vulnerable to CSRF.

### 20160113: Mert Taşçi

    The 'forgot password' link was vulnerable to reflected XSS.

### 20150907: Sandeep Singh

    An open redirect was possible by passing a URL with a mixed-case protocol as the goto parameter.

### 20150904: Manish Bhattacharya

    The site name display for stories was vulnerable to an IDN homograph attack.

### 20150827: Chris Marlow

    Revisions to HN's markup caused an HTML injection regression.

### 20150624: Stephen Sclafani

    A form handling bug led to a XSS vulnerability using HTTP parameter polution.

### 20150302: Max Bond

    Information leaked during /r processing allowed an attacker to discover valid profile edit links and the user for which they were valid.
    goto parameters functioned as open redirects.

### 20141101: Ovidiu Toader

    In rare cases some users' profiles (including email addresses and password hashes) were mistakenly published to the Firebase API.

See https://news.ycombinator.com/item?id=8604586 for details.

### 20141027: San Tran

    Some pages displaying forms were vulnerable to reflected XSS when provided malformed query string arguments.

### 20140501: Jonathan Rudenberg

    Some YC internal pages were vulnerable to persistent XSS.

### 20120801: Louis Lang

    Redirects were vulnerable to HTTP response splitting via the whence argument.
    Persistent XSS could be achieved via the X-Forwarded-For header.

### 20120720: Michael Borohovski

    Incorrect handling of unauthenticated requests meant anyone could change rsvp status for Demo Day.

### 20090603: Daniel Fox Franke

    The state of the PRNG used to generate cookies could be determined from observed outputs. This allowed an attacker to fairly easily determine valid user cookies and compromise accounts.

See https://news.ycombinator.com/item?id=639976 for details.

**Missing From This List?** If you reported a vulnerability to us and don't see your name, please shoot us an email and we'll happily add you. We crawled through tons of emails trying to find all reports but inevitably missed some. 
