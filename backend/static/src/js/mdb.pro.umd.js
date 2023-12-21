// BOOTSTRAP CORE COMPONENTS
import { Button } from './free/button.js';
import { Offcanvas } from './bootstrap/mdb-prefix/offcanvas.js';
import { Carousel } from './free/carousel.js';
import { Popover } from './free/popover.js';
import { ScrollSpy } from './free/scrollspy.js';
import { Tab } from './free/tab.js';
import { Tooltip } from './free/tooltip.js';

// MDB FREE COMPONENTS
import { Input } from './free/input.js';
import { Collapse } from './free/collapse.js';
import { Dropdown } from './free/dropdown.js';
import { Ripple } from './free/ripple.js';
import { Range } from './free/range.js';

// MDB PRO COMPONENTS
import { Animate } from './pro/animate.js';
import { Chart } from './pro/charts/charts.js';
import { Lightbox } from './pro/lightbox.js';
import { Rating } from './pro/rating.js';
import { Sidenav } from './pro/sidenav.js';
import { Alert } from './pro/alert.js';
import { Toast } from './pro/toast.js';
import { Timepicker } from './pro/timepicker/index.js';
import { Navbar } from './pro/navbar.js';
import { InfiniteScroll } from './pro/infinite-scroll.js';
import { LazyLoad } from './pro/lazy-load.js';
import { Datepicker } from './pro/datepicker/index.js';
import { Popconfirm } from './pro/popconfirm.js';
import { Datatable } from './pro/datatable/index.js';
import { Stepper } from './pro/stepper.js';
import { Sticky } from './pro/sticky.js';
import { Select } from './pro/select/index.js';
import { Touch } from './pro/touch/index.js';
import { SmoothScroll } from './pro/smooth-scroll.js';
import { PerfectScrollbar } from './pro/perfect-scrollbar.js';
import { Loading } from './pro/loading-management/index.js';
import { Autocomplete } from './pro/autocomplete/index.js';
import { Modal } from './pro/modal.js';
import { Clipboard } from './pro/clipboard.js';
import { ChipsInput } from './pro/chips/index.js';
import { Chip } from './pro/chips/chip.js';
import { MultiRangeSlider } from './pro/multi-range/index.js';
import { Datetimepicker } from './pro/date-time-picker/index.js';

import { initMDB } from './autoinit/index.pro.js';

const mdb = {
  // FREE
  Button,
  Carousel,
  Collapse,
  Offcanvas,
  Dropdown,
  Input,
  Modal,
  Popover,
  ScrollSpy,
  Ripple,
  Tab,
  Tooltip,
  Range,
  // PRO
  Alert,
  Animate,
  Chart,
  Datepicker,
  Datatable,
  Lightbox,
  Navbar,
  Popconfirm,
  Rating,
  Sidenav,
  SmoothScroll,
  Timepicker,
  Toast,
  InfiniteScroll,
  LazyLoad,
  Stepper,
  Sticky,
  Select,
  Touch,
  PerfectScrollbar,
  Loading,
  Autocomplete,
  Clipboard,
  ChipsInput,
  Chip,
  MultiRangeSlider,
  Datetimepicker,
};

initMDB(mdb);

export {
  // FREE
  Button,
  Carousel,
  Collapse,
  Offcanvas,
  Dropdown,
  Input,
  Modal,
  Popover,
  ScrollSpy,
  Ripple,
  Tab,
  Tooltip,
  Range,
  // PRO
  Alert,
  Animate,
  Chart,
  Datepicker,
  Datatable,
  Lightbox,
  Navbar,
  Popconfirm,
  Rating,
  Sidenav,
  SmoothScroll,
  Timepicker,
  Toast,
  InfiniteScroll,
  LazyLoad,
  Stepper,
  Sticky,
  Select,
  Touch,
  PerfectScrollbar,
  Loading,
  Autocomplete,
  Clipboard,
  ChipsInput,
  Chip,
  MultiRangeSlider,
  Datetimepicker,
  initMDB,
};
