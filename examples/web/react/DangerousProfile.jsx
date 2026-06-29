export function DangerousProfile({ bio }) {
  return (
    <section>
      <h1>User profile</h1>
      <div dangerouslySetInnerHTML={{ __html: bio }} />
    </section>
  );
}
