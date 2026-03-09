import 'next-auth';
import 'next-auth/jwt';

declare module 'next-auth' {
  interface Session {
    user: {
      id: string;
      name?: string | null;
      email?: string | null;
      username?: string | null;
    };
  }

  interface User {
    id: string;
    username?: string;
  }
}

declare module 'next-auth/jwt' {
  interface JWT {
    user?: {
      id: string;
      name?: string | null;
      email?: string | null;
      username?: string | null;
    };
  }
}