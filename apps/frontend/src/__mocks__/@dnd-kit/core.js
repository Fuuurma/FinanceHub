function DndContext({ sensors, collisionDetection, onDragEnd, children }) {
  return children;
}

function closestCenter(args) {
  return args;
}

function KeyboardSensor({ coordinateGetter }) {
  return { sensors: [] };
}

function PointerSensor({ activationConstraint }) {
  return { sensors: [] };
}

function useSensor(sensor, options) {
  return { ...options };
}

function useSensors(...sensors) {
  return sensors;
}

function DragEndEvent(args) {
  return args;
}

module.exports = {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
};
