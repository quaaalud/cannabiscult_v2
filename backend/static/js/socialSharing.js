class SocialSharing {
  constructor() {
    this.pageUrl = window.location.href;
    this.pageTitle = document.title;
  }

  shareOnTwitter() {
    const twitterShareUrl = `https://twitter.com/intent/tweet?url=${encodeURIComponent(this.pageUrl)}&text=${encodeURIComponent(this.pageTitle)}`;
    window.open(twitterShareUrl, '_blank');
  }
  shareOnFacebook() {
    const facebookShareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(this.pageUrl)}`;
    window.open(facebookShareUrl, '_blank');
  }
  shareOnReddit() {
    const redditShareUrl = `https://www.reddit.com/submit?url=${encodeURIComponent(this.pageUrl)}&title=${encodeURIComponent(this.pageTitle)}`;
    window.open(redditShareUrl, '_blank');
  }
  shareViaEmail() {
    if (navigator.share) {
      navigator.share({
        title: this.pageTitle,
        url: this.pageUrl
      }).catch(console.error);
    } else {
      const emailSubject = encodeURIComponent(this.pageTitle);
      const emailBody = encodeURIComponent(`Check out this page: ${this.pageUrl}`);
      window.location.href = `mailto:?subject=${emailSubject}&body=${emailBody}`;
    }
  }
  shareViaText() {
    if (navigator.share) {
      navigator.share({
        title: this.pageTitle,
        text: `Check out this page: ${this.pageTitle} - ${this.pageUrl}`,
        url: this.pageUrl
      }).catch(console.error);
    } else {
      alert('Text sharing is not supported on this device.');
    }
  }
}

export default SocialSharing;