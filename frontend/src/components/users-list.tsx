import { component$, useStore, $, useVisibleTask$} from '@builder.io/qwik';

export const UsersList = component$(() => {

  const store = useStore({
    users: [],
    error: null,
  });

  const fetchUsers = $(async () => {
    store.error = null;
    try {
      const response = await fetch('http://localhost:8000/users/');
      if (!response.ok) {
        throw new Error('Error fetching users');
      }
      const users = await response.json();
      store.users = users;
    } catch (error) {
      console.error(error);
    }
  });

  useVisibleTask$(async () => {
    fetchUsers()
  })

  return (
    <div>
      <ul>
        {store.users.map((user: any) => (
          <li key={user.dni}>{user.nombre} {user.apellido} {user.fecha_nacimiento}</li>
        ))}
      </ul>
    </div>
  );
});
