/**
 * CalendarManager manages calendar events using MDB Pro Bootstrap library.
 * It allows for adding, removing, and updating events within an MDB Calendar instance.
 */
class CalendarManager {
    /**
     * Creates an instance of CalendarManager.
     * @param {string} elementId The ID of the DOM element where the calendar will be initialized.
     */
    constructor(elementId) {
        this.element = document.getElementById(elementId);
        if (!this.element) throw new Error('Element not found');
        this.events = [
          {
              summary: 'Cannabis Cult Connoisseur Pack',
              description: 'Connoisseur Packs are Back!',
              start: '01/03/2024',
              end: '15/03/2024',
              color: { background: '#cfe0fc', foreground: '#0a47a9' },
              id: 1
          }
        ]
        calendarManager.addEvent(event);
        this.initMDBCalendar();
    }

    /**
     * Initializes the MDB Calendar component.
     */
    initMDBCalendar() {
        $(document).ready(function() {
          window.addEventListener('supabaseClientReady', async function() {
    
            // Initialize the MDB Calendar
            this.calendarInstance = new Calendar(document.getElementById(elementId), options);
    
            // Optionally, load initial events if any
            this.events.forEach(event => this.calendarInstance.addEvent(event));
        });
      });
    }
    /**
     * Adds an event to the calendar.
     * @param {Object} event The event object to add.
     */
    addEvent(event) {
        this.events.push(event);
        if (this.calendarInstance) {
            this.calendarInstance.addEvent(event);
        }
    }

    /**
     * Removes an event from the calendar by its ID.
     * @param {number|string} eventId The ID of the event to remove.
     */
    removeEvent(eventId) {
        this.events = this.events.filter(event => event.id !== eventId);
        if (this.calendarInstance) {
            this.calendarInstance.removeEvent(eventId);
        }
    }

    /**
     * Updates an existing event in the calendar.
     * @param {Object} updatedEvent The updated event object.
     */
    updateEvent(updatedEvent) {
        const index = this.events.findIndex(event => event.id === updatedEvent.id);
        if (index !== -1) {
            this.events[index] = updatedEvent;
            if (this.calendarInstance) {
                this.calendarInstance.updateEvent(updatedEvent);
            }
        }
    }

}
