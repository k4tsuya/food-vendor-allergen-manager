import CodeLabelAdmin from './CodeLabelAdmin';

function AdminCategoriesPage() {
  return <CodeLabelAdmin title="Categories" singularLabel="category" apiPath="/categories" />;
}

export default AdminCategoriesPage;