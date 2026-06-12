import { createClient, createAccount as createGenLayerAccount, generatePrivateKey } from "genlayer-js";
import { localnet } from "genlayer-js/chains";

const normalizePrivateKey = (key) => (key.startsWith("0x") ? key : `0x${key}`);

const storedKey = localStorage.getItem("accountPrivateKey");
export const account = storedKey ? createGenLayerAccount(normalizePrivateKey(storedKey)) : null;

export const createAccount = () => {
  const newAccountPrivateKey = generatePrivateKey();
  localStorage.setItem("accountPrivateKey", newAccountPrivateKey);
  return createGenLayerAccount(newAccountPrivateKey);
};

export const removeAccount = () => {
  localStorage.removeItem("accountPrivateKey");
};

export const client = createClient({ chain: localnet, account });
