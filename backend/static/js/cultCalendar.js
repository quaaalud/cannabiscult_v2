/**
 * CalendarManager manages calendar events using MDB Pro Bootstrap library.
 * It allows for adding, removing, and updating events within an MDB Calendar instance.
 */
export class CalendarManager {
    constructor(eventsList) {
        this.elementId = 'calendar';
        this.element = document.getElementById(this.elementId);
        if (!this.element) throw new Error('Element not found');
        this.colorPalette = [
            { background: '#BBDEFB', foreground: '#0D47A1' },
            { background: '#90A4AE', foreground: '#000000' },
            { background: '#B3E5FC', foreground: '#01579B' },
            { background: '#B2EBF2', foreground: '#006064' },
            { background: '#B2DFDB', foreground: '#004D40' },
            { background: '#E0F7FA', foreground: '#00695C' },
            { background: '#ECEFF1', foreground: '#263238' },
            { background: '#E0F2F1', foreground: '#004D40' },
            { background: '#CFD8DC', foreground: '#37474F' },
            { background: '#B0BEC5', foreground: '#263238' }
        ];
        this.colorIndex = Math.floor(Math.random() * this.colorPalette.length);
        this.eventsList = eventsList || [];
        this.events = [];
        this.processEvents();
        this.initMDBCalendar();
    }
    /**
     * Factory method to create an instance asynchronously.
     * @returns {Promise<CalendarManager>}
     */
    static async create() {
        const eventsList = await CalendarManager.fetchEvents();
        return new CalendarManager(eventsList);
    }
    /**
     * Fetches events from the API.
     * @returns {Promise<Array>}
     */
    static async fetchEvents() {
        try {
            const response = await fetch('/search/get-all-events/');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error("Failed to load events:", error);
            return []; // Return an empty array if fetch fails
        }
    }
    /**
     * Initializes the MDB Calendar component.
     */
    initMDBCalendar() {
        const spinnerRow = document.getElementById('spinnerRow');
        const spinner = this.element.querySelector('.spinner-border');
        this.calendarInstance = new Calendar(this.element, {
            readonly: true,
        });
        if (spinner ) {
            spinner.remove();
            spinnerRow.classList.add('d-none');
        }
        if (this.events.length > 0) {
            this.calendarInstance.addEvents(this.events);
        }
        this.calendarInstance.refresh();
    }
    /**
     * Creates and adds an event to the calendar and internal events array.
     * @param {string} summary - Event title.
     * @param {string} description - Event details.
     * @param {string} startDate - Start date in YYYY-MM-DD format.
     * @param {string} endDate - End date in YYYY-MM-DD format.
     */
    createEvent(summary, description, startDate, endDate) {
        const color = this.colorPalette[this.colorIndex];
        this.colorIndex = (this.colorIndex + 1) % this.colorPalette.length; // Rotate colors
        const formattedEvent = {
            summary,
            description,
            start: { date: startDate, datetime: `${startDate}T09:00:00` },
            end: { date: endDate, datetime: `${endDate}T09:00:00` },
            color,
            id: Math.random().toString(36).substr(2, 9) // Generate unique ID
        };

        this.events.push(formattedEvent);
    }
    /**
     * Processes events and adds them to the internal events array.
     */
    processEvents() {
        this.eventsList.forEach(event => {
            this.createEvent(event.summary, event.description, event.start_date, event.end_date);
        });
    }
}
