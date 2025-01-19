export class SimpleTypewriter {
  /**
   * A more robust, accessible Typewriter effect class.
   *
   * Example usage:
   *
   *   import { SimpleTypewriter } from './typewriter.js';
   *
   *   const typewriter = new SimpleTypewriter({
   *     targetId: 'typewriterText',
   *     phrases: ['Join the Cult', 'Sign Up Today', 'Become a Member'],
   *     typingSpeed: 100,
   *     pauseDuration: 1500,
   *     ariaLive: 'polite',
   *     respectReducedMotion: true
   *   });
   *   typewriter.start();
   */
  constructor(options) {
    const {
      targetId,
      phrases,
      typingSpeed = 100,
      pauseDuration = 1500,
      ariaLive = 'polite',
      backspace = true,
      respectReducedMotion = true
    } = options;

    // Required fields
    if (!targetId || !Array.isArray(phrases)) {
      throw new Error('Typewriter: "targetId" and "phrases" are required options.');
    }

    this.targetElem = document.getElementById(targetId);
    if (!this.targetElem) {
      throw new Error(`Typewriter: No element found with ID "${targetId}".`);
    }

    // Store options
    this.phrases = phrases;
    this.typingSpeed = typingSpeed;
    this.pauseDuration = pauseDuration;
    this.ariaLive = ariaLive;
    this.backspace = backspace;
    this.respectReducedMotion = respectReducedMotion;

    // Initialize state
    this.phraseIndex = 0;
    this.charIndex = 0;
    this.isAnimating = false;
    this.isSkipping = false;
    this.timeoutId = null;  // Will store the current setTimeout ID for safety

    // Set aria-live for accessibility
    this.targetElem.setAttribute('aria-live', this.ariaLive);

    // Check user preference for reduced motion
    this.prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }

  /**
   * Start or resume the typewriter effect from the current phrase/char index.
   * If already animating, calling this again has no effect.
   */
  start() {
    if (this.isAnimating) return;
    this.isAnimating = true;

    // Optionally clear existing text if you always want to type from empty:
    // this.targetElem.textContent = ''; 

    this.typeCharacter();
  }

  /**
   * Stop the animation (immediately).
   * The text remains as-is in the DOM, but no more typing or backspacing occurs.
   */
  stop() {
    this.isAnimating = false;
    this.isSkipping = false;

    // Clear any pending timeouts
    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
      this.timeoutId = null;
    }
  }

  /**
   * Completely clear the text, reset indexes, and stop the animation.
   * Useful if you want to fully restart or change phrases without leftover text.
   */
  reset() {
    this.stop();
    this.targetElem.textContent = '';
    this.phraseIndex = 0;
    this.charIndex = 0;
  }

  /**
   * Provide a new set of phrases on-the-fly.
   * Optionally restart immediately with the new phrases from scratch.
   * @param {string[]} newPhrases - The new array of phrases to type
   * @param {boolean} [startImmediately=false] - If true, reset and start animation immediately
   */
  setPhrases(newPhrases, startImmediately = false) {
    if (!Array.isArray(newPhrases)) {
      throw new Error('Typewriter: newPhrases must be an array of strings.');
    }

    // Update the phrases
    this.phrases = newPhrases;

    // Optionally reset the internal indices and text
    this.reset();

    // If requested, start right away with the new phrases
    if (startImmediately) {
      this.start();
    }
  }

  /**
   * Skip the animation and instantly display the current phrase.
   * Then proceed to the next cycle without animation.
   */
  skip() {
    this.isSkipping = true;
  }

  /**
   * Erase existing text, remove references, etc.
   * If you never plan to reuse this instance, call destroy().
   */
  destroy() {
    this.stop();
    this.targetElem.textContent = '';
  }

  /**
   * Internal helper to type characters one by one.
   */
  typeCharacter() {
    // If we've been told to stop or skip
    if (!this.isAnimating) return;

    // If user wants to skip or we have to respect reduced motion, instantly place full phrase
    if (this.isSkipping || (this.respectReducedMotion && this.prefersReducedMotion)) {
      this.instantFillPhrase();
      return;
    }

    const currentPhrase = this.phrases[this.phraseIndex];
    // If we still have characters to type...
    if (this.charIndex < currentPhrase.length) {
      this.targetElem.textContent += currentPhrase.charAt(this.charIndex);
      this.charIndex++;
      this.timeoutId = setTimeout(() => this.typeCharacter(), this.typingSpeed);
    } else {
      // Once phrase is fully typed, pause, then proceed
      this.timeoutId = setTimeout(() => {
        this.prepareNextPhrase();
      }, this.pauseDuration);
    }
  }

  /**
   * Immediately fill the current phrase (for skipping or reduced motion).
   */
  instantFillPhrase() {
    const currentPhrase = this.phrases[this.phraseIndex];
    this.targetElem.textContent = currentPhrase;

    this.timeoutId = setTimeout(() => {
      this.prepareNextPhrase();
    }, this.pauseDuration);
  }

  /**
   * Prepare to move on to the next phrase. Optionally backspaces first.
   */
  prepareNextPhrase() {
    if (!this.isAnimating) return;

    // If we are skipping or there's no backspace step, jump directly
    if (this.isSkipping || !this.backspace) {
      this.isSkipping = false;
      this.advancePhraseIndex();
      return;
    }

    // Otherwise, erase text
    this.eraseCharacter();
  }

  /**
   * Erase text one character at a time.
   */
  eraseCharacter() {
    if (!this.isAnimating) return;

    if (this.targetElem.textContent.length > 0) {
      this.targetElem.textContent = this.targetElem.textContent.slice(0, -1);
      this.timeoutId = setTimeout(() => this.eraseCharacter(), 30);
    } else {
      this.advancePhraseIndex();
    }
  }

  /**
   * Move to the next phrase and start typing again (if multiple phrases).
   */
  advancePhraseIndex() {
    this.isSkipping = false;
    this.phraseIndex = (this.phraseIndex + 1) % this.phrases.length;
    this.charIndex = 0;
    this.typeCharacter();
  }
}
