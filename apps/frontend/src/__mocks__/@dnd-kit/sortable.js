function useSortable({ id, disabled }) {
  return {
    attributes: {},
    listeners: disabled ? {} : { draggable: 'true' },
    setNodeRef: () => {},
    transform: null,
    transition: null,
    isDragging: false,
  };
}

function SortableContext({ items, strategy, children }) {
  return children;
}

function arrayMove(array, from, to) {
  const newArray = [...array];
  const [item] = newArray.splice(from, 1);
  newArray.splice(to, 0, item);
  return newArray;
}

function sortableKeyboardCoordinates(event) {
  return [event];
}

function verticalListSortingStrategy(items) {
  return items;
}

function rectSortingStrategy(items) {
  return items;
}

module.exports = {
  useSortable,
  SortableContext,
  arrayMove,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
  rectSortingStrategy,
};
