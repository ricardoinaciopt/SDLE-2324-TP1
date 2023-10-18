list_schema = {
  type: "object",
  properties: {
    version: { type: "string" },
    list: {
      type: "array",
      items: {
        type: "object",
        properties: {
          id: { type: "string" },
          acquired: { type: "boolean" },
          quantity: { type: "integer" },
        },
        required: ["id", "acquired", "quantity"],
      },
    },
  },
  required: ["version", "list"],
};

list_item_schema = {
  type: "object",
  properties: {
    id: { type: "string" },
    acquired: { type: "boolean" },
    quantity: { type: "integer" },
  },
  required: ["id", "acquired", "quantity"],
};
